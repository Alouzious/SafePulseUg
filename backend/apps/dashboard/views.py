import logging
from datetime                   import timedelta
from django.utils               import timezone
from django.db.models           import Count, Q
from rest_framework             import status
from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils      import extend_schema, OpenApiParameter

from apps.crimes.models         import CrimeReport, CrimeCategory, CrimeSeverity, CrimeStatus
from apps.analysis.models       import AnalysisResult
from apps.reports.models        import GeneratedReport
from apps.accounts.models       import OfficerUser

logger = logging.getLogger('apps.dashboard')


# ─────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────
def get_date_range(period):
    now = timezone.now()
    if period == 'week':
        return now - timedelta(days=7)
    elif period == 'month':
        return now - timedelta(days=30)
    elif period == 'year':
        return now - timedelta(days=365)
    return None


# ─────────────────────────────────────────────────────────────
# OVERVIEW
# ────────────────────────────────────────────────────���────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get main dashboard overview statistics',
    description='Returns total crimes, status breakdown, solve rate, and system-wide stats.',
)
class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now         = timezone.now()
        last_7days  = now - timedelta(days=7)
        last_30days = now - timedelta(days=30)

        total_crimes        = CrimeReport.objects.count()
        crimes_this_week    = CrimeReport.objects.filter(date_reported__gte=last_7days).count()
        crimes_this_month   = CrimeReport.objects.filter(date_reported__gte=last_30days).count()
        reported            = CrimeReport.objects.filter(status=CrimeStatus.REPORTED).count()
        under_investigation = CrimeReport.objects.filter(status=CrimeStatus.UNDER_INVESTIGATION).count()
        solved              = CrimeReport.objects.filter(status=CrimeStatus.SOLVED).count()
        cold_cases          = CrimeReport.objects.filter(status=CrimeStatus.COLD_CASE).count()
        high_priority       = CrimeReport.objects.filter(
                                severity__in=['high', 'critical'],
                                status__in=['reported', 'under_investigation']
                              ).count()
        total_analyses      = AnalysisResult.objects.filter(status='completed').count()
        total_reports       = GeneratedReport.objects.count()
        total_officers      = OfficerUser.objects.filter(is_active=True).count()
        solve_rate          = round((solved / total_crimes * 100), 1) if total_crimes > 0 else 0

        return Response({
            'crimes': {
                'total':              total_crimes,
                'this_week':          crimes_this_week,
                'this_month':         crimes_this_month,
                'high_priority':      high_priority,
                'solve_rate_percent': solve_rate,
            },
            'by_status': {
                'reported':             reported,
                'under_investigation':  under_investigation,
                'solved':               solved,
                'cold_cases':           cold_cases,
            },
            'system': {
                'total_analyses':  total_analyses,
                'total_reports':   total_reports,
                'active_officers': total_officers,
            },
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# BY CATEGORY
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get crimes grouped by category',
    parameters=[
        OpenApiParameter('period', str, description='Filter period: week, month, year, all'),
    ]
)
class CrimesByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        since  = get_date_range(period)
        crimes = CrimeReport.objects.all()
        if since:
            crimes = crimes.filter(date_reported__gte=since)
        data = crimes.values('category').annotate(count=Count('id')).order_by('-count')
        result = [
            {
                'category': item['category'].replace('_', ' ').title(),
                'value':    item['category'],
                'count':    item['count'],
            }
            for item in data
        ]
        return Response({'period': period, 'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# HOTSPOTS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get crime hotspots by district',
    parameters=[
        OpenApiParameter('period', str, description='Filter period: week, month, year, all'),
        OpenApiParameter('limit',  int, description='Number of top districts to return (default 10)'),
    ]
)
class CrimeHotspotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        since  = get_date_range(period)
        limit  = int(request.query_params.get('limit', 10))
        crimes = CrimeReport.objects.all()
        if since:
            crimes = crimes.filter(date_reported__gte=since)
        data = (
            crimes
            .values('district')
            .annotate(
                total         = Count('id'),
                high_severity = Count('id', filter=Q(severity__in=['high', 'critical'])),
                unsolved      = Count('id', filter=Q(status__in=['reported', 'under_investigation'])),
            )
            .order_by('-total')[:limit]
        )
        result = [
            {
                'district':      item['district'],
                'total':         item['total'],
                'high_severity': item['high_severity'],
                'unsolved':      item['unsolved'],
                'risk_level': (
                    'critical' if item['high_severity'] >= 5
                    else 'high'   if item['high_severity'] >= 3
                    else 'medium' if item['total']        >= 3
                    else 'low'
                ),
            }
            for item in data
        ]
        return Response({'period': period, 'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# MONTHLY TRENDS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get monthly crime trends for the last 12 months',
    description='Returns crime counts grouped by month for the past 12 months.',
)
class MonthlyTrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncMonth

        since = timezone.now() - timedelta(days=365)
        data  = (
            CrimeReport.objects
            .filter(date_reported__gte=since)
            .annotate(month=TruncMonth('date_reported'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        result = [
            {
                'month': item['month'].strftime('%b %Y'),
                'count': item['count'],
            }
            for item in data
        ]
        return Response({'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# DAILY TRENDS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get daily crime trends for the last 30 days',
    description='Returns crime counts per day for the past 30 days.',
)
class DailyTrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models.functions import TruncDate

        since = timezone.now() - timedelta(days=30)
        data  = (
            CrimeReport.objects
            .filter(date_reported__gte=since)
            .annotate(date=TruncDate('date_reported'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        result = [
            {
                'date':  item['date'].strftime('%Y-%m-%d'),
                'count': item['count'],
            }
            for item in data
        ]
        return Response({'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# BY SEVERITY
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get crimes grouped by severity',
    description='Returns crime counts for each severity level with color codes for React charts.',
    parameters=[
        OpenApiParameter('period', str, description='Filter period: week, month, year, all'),
    ]
)
class CrimesBySeverityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', 'all')
        since  = get_date_range(period)
        crimes = CrimeReport.objects.all()
        if since:
            crimes = crimes.filter(date_reported__gte=since)

        data = crimes.values('severity').annotate(count=Count('id')).order_by('-count')

        color_map = {
            'low':      '#16a34a',
            'medium':   '#f97316',
            'high':     '#dc2626',
            'critical': '#7c3aed',
        }
        result = [
            {
                'severity': item['severity'].title(),
                'value':    item['severity'],
                'count':    item['count'],
                'color':    color_map.get(item['severity'], '#6b7280'),
            }
            for item in data
        ]
        return Response({'period': period, 'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# RECENT CRIMES
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get the latest crime reports feed',
    description='Returns the most recently reported crimes for the dashboard live feed.',
    parameters=[
        OpenApiParameter('limit', int, description='Number of recent crimes to return (default 10)'),
    ]
)
class RecentCrimesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit   = int(request.query_params.get('limit', 10))
        reports = (
            CrimeReport.objects
            .select_related('reported_by')
            .order_by('-date_reported')[:limit]
        )
        result = [
            {
                'id':            r.id,
                'case_number':   r.case_number,
                'title':         r.title,
                'category':      r.category.replace('_', ' ').title(),
                'severity':      r.severity,
                'status':        r.status.replace('_', ' ').title(),
                'district':      r.district,
                'date_reported': r.date_reported.strftime('%Y-%m-%d %H:%M'),
                'is_analyzed':   r.is_analyzed,
                'reported_by':   r.reported_by.full_name if r.reported_by else 'Unknown',
            }
            for r in reports
        ]
        return Response({'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get high priority unresolved crime alerts',
    description='Returns unsolved high and critical severity crimes that need immediate attention.',
)
class AlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = (
            CrimeReport.objects
            .filter(
                severity__in=['high', 'critical'],
                status__in=['reported', 'under_investigation']
            )
            .select_related('reported_by')
            .order_by('-date_reported')[:10]
        )
        result = [
            {
                'id':            r.id,
                'case_number':   r.case_number,
                'title':         r.title,
                'category':      r.category.replace('_', ' ').title(),
                'severity':      r.severity,
                'status':        r.status.replace('_', ' ').title(),
                'district':      r.district,
                'date_reported': r.date_reported.strftime('%Y-%m-%d %H:%M'),
                'days_open':     (timezone.now() - r.date_reported).days,
            }
            for r in alerts
        ]
        return Response({'count': len(result), 'data': result}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# OFFICER PERSONAL STATS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get personal statistics for the logged-in officer',
    description='Returns the officer profile summary, their submitted crimes, and activity stats.',
)
class OfficerStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        officer        = request.user
        my_reports     = CrimeReport.objects.filter(reported_by=officer)
        my_analyses    = AnalysisResult.objects.filter(requested_by=officer)
        my_gen_reports = GeneratedReport.objects.filter(generated_by=officer)

        my_by_status = (
            my_reports
            .values('status')
            .annotate(count=Count('id'))
        )
        my_by_category = (
            my_reports
            .values('category')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        return Response({
            'officer': {
                'name':         officer.full_name,
                'badge_number': officer.badge_number,
                'rank':         officer.rank,
                'station':      officer.station,
            },
            'my_crimes': {
                'total':       my_reports.count(),
                'by_status':   list(my_by_status),
                'by_category': list(my_by_category),
            },
            'my_activity': {
                'total_analyses':          my_analyses.count(),
                'total_reports_generated': my_gen_reports.count(),
            },
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────���──────
# CATEGORY VS DISTRICT
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['📊 Dashboard'],
    summary='Get crime counts broken down by category and district',
    description='Useful for building heatmaps and cross-filter charts in React.',
    parameters=[
        OpenApiParameter('category', str, description='Filter by specific crime category'),
        OpenApiParameter('district', str, description='Filter by specific district name'),
    ]
)
class CategoryDistrictView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        district = request.query_params.get('district')

        crimes = CrimeReport.objects.all()
        if category:
            crimes = crimes.filter(category=category)
        if district:
            crimes = crimes.filter(district__icontains=district)

        data = (
            crimes
            .values('category', 'district')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
        result = [
            {
                'category': item['category'].replace('_', ' ').title(),
                'district': item['district'],
                'count':    item['count'],
            }
            for item in data
        ]
        return Response({'data': result}, status=status.HTTP_200_OK)