from django.urls import path
from .views import (
    CrimeReportListCreateView,
    CrimeReportDetailView,
    MyReportsView,
    SuspectView,
    WitnessView,
    CrimeStatsView,
)
from .upload_views import (
    CrimeBulkUploadView,
    CrimeUploadTemplateView,
)

urlpatterns = [
    # ── Core CRUD ───────────────────────────────────────────
    path('',                    CrimeReportListCreateView.as_view(), name='crime-list-create'),
    path('<int:pk>/',            CrimeReportDetailView.as_view(),    name='crime-detail'),
    path('my-reports/',          MyReportsView.as_view(),            name='my-reports'),
    path('stats/',               CrimeStatsView.as_view(),           name='crime-stats'),

    # ── Bulk Upload ─────────────────────────────────────────
    path('upload/',              CrimeBulkUploadView.as_view(),      name='crime-bulk-upload'),
    path('upload/template/',     CrimeUploadTemplateView.as_view(),  name='crime-upload-template'),

    # ── Suspects & Witnesses ────────────────────────────────
    path('<int:pk>/suspects/',          SuspectView.as_view(), name='crime-suspects'),
    path('<int:pk>/suspects/<int:sid>/', SuspectView.as_view(), name='crime-suspect-detail'),
    path('<int:pk>/witnesses/',          WitnessView.as_view(), name='crime-witnesses'),
    path('<int:pk>/witnesses/<int:wid>/', WitnessView.as_view(), name='crime-witness-detail'),
]