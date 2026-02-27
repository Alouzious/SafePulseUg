from django.urls import path
from .views import (
    AnalyzeCrimeReportView,
    GeneralAnalysisView,
    AgentChatView,
    AnalysisResultsListView,
    AnalysisResultDetailView,
)

urlpatterns = [
    # Analysis endpoints
    path('analyze-report/', AnalyzeCrimeReportView.as_view(),   name='analyze-report'),
    path('general/',        GeneralAnalysisView.as_view(),       name='general-analysis'),

    # Chat with agent
    path('chat/',                       AgentChatView.as_view(), name='agent-chat'),
    path('chat/<str:session_id>/',      AgentChatView.as_view(), name='agent-chat-history'),

    # Results
    path('results/',        AnalysisResultsListView.as_view(),  name='analysis-results'),
    path('results/<int:pk>/', AnalysisResultDetailView.as_view(), name='analysis-result-detail'),
]