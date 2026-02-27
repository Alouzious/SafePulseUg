import logging
from rest_framework                 import status, generics, filters
from rest_framework.views           import APIView
from rest_framework.response        import Response
from rest_framework.permissions     import IsAuthenticated
from rest_framework.parsers         import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils          import extend_schema, OpenApiParameter

from .models import CrimeReport, Suspect, Witness
from .serializers import (
    CrimeReportListSerializer,
    CrimeReportDetailSerializer,
    CrimeReportCreateSerializer,
    CrimeReportUpdateSerializer,
    SuspectSerializer,
    WitnessSerializer,
)

logger = logging.getLogger('apps.crimes')


# ─────────────────────────────────────────────────────────────
# CRIME REPORT LIST & CREATE
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='List all crime reports or submit a new one',
    parameters=[
        OpenApiParameter('category', str, description='Filter by crime category (theft, assault, robbery...)'),
        OpenApiParameter('status',   str, description='Filter by status (reported, solved...)'),
        OpenApiParameter('district', str, description='Filter by district name'),
        OpenApiParameter('severity', str, description='Filter by severity (low, medium, high, critical)'),
        OpenApiParameter('search',   str, description='Search in title, description, or case number'),
    ]
)
class CrimeReportListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        reports  = CrimeReport.objects.all()
        category = request.query_params.get('category')
        status_  = request.query_params.get('status')
        district = request.query_params.get('district')
        severity = request.query_params.get('severity')
        search   = request.query_params.get('search')

        if category:
            reports = reports.filter(category=category)
        if status_:
            reports = reports.filter(status=status_)
        if district:
            reports = reports.filter(district__icontains=district)
        if severity:
            reports = reports.filter(severity=severity)
        if search:
            reports = (
                reports.filter(title__icontains=search)
                | reports.filter(description__icontains=search)
                | reports.filter(case_number__icontains=search)
            )

        serializer = CrimeReportListSerializer(reports, many=True)
        return Response({
            'count':   reports.count(),
            'results': serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CrimeReportCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            crime_report = serializer.save()
            logger.info(
                f"New crime report created: {crime_report.case_number} "
                f"by {request.user.badge_number}"
            )
            return Response({
                'message': 'Crime report submitted successfully.',
                'report':  CrimeReportDetailSerializer(crime_report).data,
            }, status=status.HTTP_201_CREATED)
        logger.warning(f"Crime report creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# CRIME REPORT DETAIL
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Get, update or delete a crime report',
)
class CrimeReportDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return CrimeReport.objects.get(pk=pk)
        except CrimeReport.DoesNotExist:
            return None

    def get(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Crime report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            CrimeReportDetailSerializer(report).data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Crime report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CrimeReportUpdateSerializer(
            report, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Crime report updated: {report.case_number}")
            return Response({
                'message': 'Crime report updated successfully.',
                'report':  CrimeReportDetailSerializer(report).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        report = self.get_object(pk)
        if not report:
            return Response(
                {'error': 'Crime report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        if not request.user.is_admin and report.reported_by != request.user:
            return Response(
                {'error': 'You do not have permission to delete this report.'},
                status=status.HTTP_403_FORBIDDEN
            )
        case_number = report.case_number
        report.delete()
        logger.info(f"Crime report deleted: {case_number} by {request.user.badge_number}")
        return Response(
            {'message': f'Crime report {case_number} deleted successfully.'},
            status=status.HTTP_200_OK
        )


# ─────────────────────────────────────────────────────────────
# MY REPORTS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Get crime reports submitted by the logged-in officer',
)
class MyReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports    = CrimeReport.objects.filter(reported_by=request.user)
        serializer = CrimeReportListSerializer(reports, many=True)
        return Response({
            'count':   reports.count(),
            'results': serializer.data,
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────
# SUSPECTS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Add or remove a suspect from a crime report',
)
class SuspectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            report = CrimeReport.objects.get(pk=pk)
        except CrimeReport.DoesNotExist:
            return Response(
                {'error': 'Crime report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SuspectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(crime_report=report)
            logger.info(f"Suspect added to case: {report.case_number}")
            return Response({
                'message': 'Suspect added successfully.',
                'suspect': serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, sid):
        try:
            suspect = Suspect.objects.get(pk=sid, crime_report__pk=pk)
            suspect.delete()
            return Response(
                {'message': 'Suspect removed successfully.'},
                status=status.HTTP_200_OK
            )
        except Suspect.DoesNotExist:
            return Response(
                {'error': 'Suspect not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


# ─────────────────────────────────────────────────────────────
# WITNESSES
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Add or remove a witness from a crime report',
)
class WitnessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            report = CrimeReport.objects.get(pk=pk)
        except CrimeReport.DoesNotExist:
            return Response(
                {'error': 'Crime report not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = WitnessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(crime_report=report)
            logger.info(f"Witness added to case: {report.case_number}")
            return Response({
                'message': 'Witness added successfully.',
                'witness': serializer.data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, wid):
        try:
            witness = Witness.objects.get(pk=wid, crime_report__pk=pk)
            witness.delete()
            return Response(
                {'message': 'Witness removed successfully.'},
                status=status.HTTP_200_OK
            )
        except Witness.DoesNotExist:
            return Response(
                {'error': 'Witness not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


# ─────────────────────────────────────────────────────────────
# CRIME STATS
# ─────────────────────────────────────────────────────────────
@extend_schema(
    tags=['🚔 Crimes'],
    summary='Get crime statistics summary',
    description='Returns crime counts grouped by category, status, severity and district.',
)
class CrimeStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Count
        total       = CrimeReport.objects.count()
        by_category = CrimeReport.objects.values('category').annotate(count=Count('id'))
        by_status   = CrimeReport.objects.values('status').annotate(count=Count('id'))
        by_severity = CrimeReport.objects.values('severity').annotate(count=Count('id'))
        by_district = CrimeReport.objects.values('district').annotate(count=Count('id'))
        return Response({
            'total_reports': total,
            'by_category':   list(by_category),
            'by_status':     list(by_status),
            'by_severity':   list(by_severity),
            'by_district':   list(by_district),
        }, status=status.HTTP_200_OK)