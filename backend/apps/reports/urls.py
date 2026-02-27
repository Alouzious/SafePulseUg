from django.urls import path
from .views import (
    CrimeListReportView,
    SingleCrimeReportView,
    AnalysisReportView,
    ReportHistoryView,
)
from .models import ReportFormat

urlpatterns = [
    # Crime list reports
    path('crime-list/pdf/',   CrimeListReportView.as_view(),
         {'format_type': ReportFormat.PDF},   name='crime-list-pdf'),

    path('crime-list/excel/', CrimeListReportView.as_view(),
         {'format_type': ReportFormat.EXCEL}, name='crime-list-excel'),

    # Single crime report
    path('crime/<str:case_number>/pdf/', SingleCrimeReportView.as_view(),
         name='single-crime-pdf'),

    # Analysis report
    path('analysis/<int:pk>/pdf/', AnalysisReportView.as_view(),
         name='analysis-pdf'),

    # History
    path('history/', ReportHistoryView.as_view(), name='report-history'),
]