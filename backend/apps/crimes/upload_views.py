import logging
import pandas as pd
from io                         import StringIO, BytesIO
from datetime                   import datetime
from django.utils               import timezone
from rest_framework             import status
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers     import MultiPartParser, FormParser
from drf_spectacular.utils      import extend_schema

from .models        import CrimeReport, CrimeCategory, CrimeSeverity

logger = logging.getLogger('apps.crimes')


# ─────────────────────────────────────────────────────────────
# VALID CHOICES
# ─────────────────────────────────────────────────────────────
VALID_CATEGORIES = [
    'theft', 'assault', 'homicide', 'fraud', 'cybercrime',
    'robbery', 'burglary', 'drug_offense', 'sexual_offense',
    'vandalism', 'kidnapping', 'arson', 'corruption', 'other'
]
VALID_SEVERITIES = ['low', 'medium', 'high', 'critical']


# ─────────────────────────────────────────────────────────────
# HELPER — Parse a date string flexibly
# ─────────────────────────────────────────────────────────────
def parse_date(date_str):
    if not date_str or pd.isna(date_str):
        return timezone.now()
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(str(date_str).strip(), fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    return timezone.now()


# ─────────────────────────────────────────────────────────────
# HELPER — Clean and validate a row
# ─────────────────────────────────────────────────────────────
def clean_row(row):
    category = str(row.get('category', 'other')).strip().lower()
    severity = str(row.get('severity', 'medium')).strip().lower()

    if category not in VALID_CATEGORIES:
        category = 'other'
    if severity not in VALID_SEVERITIES:
        severity = 'medium'

    return {
        'title':          str(row.get('title',          'Untitled Crime')).strip()[:200],
        'category':       category,
        'severity':       severity,
        'description':    str(row.get('description',    'No description provided')).strip(),
        'location':       str(row.get('location',       'Unknown')).strip()[:200],
        'district':       str(row.get('district',       'Unknown')).strip()[:100],
        'date_occurred':  parse_date(row.get('date_occurred')),
        'victim_count':   int(row.get('victim_count',   1)) if str(row.get('victim_count', 1)).isdigit() else 1,
        'weapons_used':   str(row.get('weapons_used',   '')).strip() if pd.notna(row.get('weapons_used')) else '',
        'modus_operandi': str(row.get('modus_operandi', '')).strip() if pd.notna(row.get('modus_operandi')) else '',
        'victim_details': str(row.get('victim_details', '')).strip() if pd.notna(row.get('victim_details')) else '',
        'evidence_notes': str(row.get('evidence_notes', '')).strip() if pd.notna(row.get('evidence_notes')) else '',
    }


# ─────────────────────────────────────────────────────────────
# CSV / EXCEL BULK UPLOAD
# POST /api/crimes/upload/
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Bulk upload crimes from CSV or Excel file',
    description='''
Upload a CSV or Excel file containing multiple crime records.

**Required columns:** title, category, severity, description, location, district, date_occurred

**Optional columns:** victim_count, weapons_used, modus_operandi, victim_details, evidence_notes

**Valid categories:** theft, assault, homicide, fraud, cybercrime, robbery, burglary,
drug_offense, sexual_offense, vandalism, kidnapping, arson, corruption, other

**Valid severities:** low, medium, high, critical

**Date format:** YYYY-MM-DD HH:MM:SS or YYYY-MM-DD
    '''
)
class CrimeBulkUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {'error': 'No file provided. Upload a CSV or Excel file.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        filename = file.name.lower()

        # ── Read the file ────────────────────────────────────
        try:
            if filename.endswith('.csv'):
                content = file.read().decode('utf-8', errors='ignore')
                df      = pd.read_csv(StringIO(content))

            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file.read()))

            else:
                return Response(
                    {'error': 'Invalid file type. Only CSV and Excel (.xlsx, .xls) are supported.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': f'Failed to read file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Validate required columns ────────────────────────
        required_cols = ['title', 'category', 'severity', 'description', 'location', 'district', 'date_occurred']
        missing_cols  = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return Response(
                {
                    'error':           f'Missing required columns: {missing_cols}',
                    'your_columns':    list(df.columns),
                    'required_columns': required_cols,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Process rows ─────────────────────────────────────
        created   = []
        skipped   = []
        errors    = []

        for idx, row in df.iterrows():
            row_num = idx + 2   # +2 for header row and 0-indexing

            try:
                # Skip completely empty rows
                if row.get('title', '') == '' or pd.isna(row.get('title', '')):
                    skipped.append({'row': row_num, 'reason': 'Empty title'})
                    continue

                data = clean_row(row)

                crime = CrimeReport.objects.create(
                    reported_by     = request.user,
                    status          = 'reported',
                    is_analyzed     = False,
                    **data
                )

                created.append({
                    'row':         row_num,
                    'case_number': crime.case_number,
                    'title':       crime.title,
                    'category':    crime.category,
                    'severity':    crime.severity,
                    'district':    crime.district,
                })

                logger.info(f"Bulk upload: created {crime.case_number}")

            except Exception as e:
                errors.append({
                    'row':    row_num,
                    'title':  str(row.get('title', 'Unknown')),
                    'error':  str(e),
                })
                logger.error(f"Bulk upload row {row_num} error: {e}")

        # ── Summary response ─────────────────────────────────
        logger.info(
            f"Bulk upload complete: {len(created)} created, "
            f"{len(skipped)} skipped, {len(errors)} errors "
            f"by {request.user.badge_number}"
        )

        return Response({
            'message':        f'Upload complete! {len(created)} crimes imported.',
            'summary': {
                'total_rows':    len(df),
                'created':       len(created),
                'skipped':       len(skipped),
                'errors':        len(errors),
            },
            'created_cases':  created,
            'skipped_rows':   skipped,
            'error_rows':     errors,
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────────
# DOWNLOAD SAMPLE CSV TEMPLATE
# GET /api/crimes/upload/template/
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Download a sample CSV template for bulk upload',
)
class CrimeUploadTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.http import HttpResponse

        sample_csv = """title,category,severity,description,location,district,date_occurred,victim_count,weapons_used,modus_operandi
Armed Robbery at Shop,robbery,high,Armed men robbed a shop at gunpoint,Kampala Road,Kampala,2026-01-15 14:30:00,2,Pistol,Entered pretending to be customers
Phone Theft at Market,theft,medium,Pickpocket stole phone from market,Owino Market,Kampala,2026-01-16 10:00:00,1,None,Distracted victim in crowd
Assault at Night,assault,high,Victim attacked by group at night,Ntinda Stage,Kampala,2026-01-17 22:00:00,1,Knives,Ambushed near bus stop
Bank Fraud,fraud,critical,Employee stole funds from accounts,Stanbic Bank,Kampala,2026-01-18 09:00:00,10,None,Used fake credentials
Drug Trafficking,drug_offense,critical,Drugs found at border post,Malaba Border,Tororo,2026-01-19 06:00:00,5,None,Hidden in cargo
"""
        response = HttpResponse(sample_csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="crime_upload_template.csv"'
        return response