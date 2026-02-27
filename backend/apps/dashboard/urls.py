from django.urls import path
from .views import (
    DashboardOverviewView,
    CrimesByCategoryView,
    CrimeHotspotsView,
    MonthlyTrendsView,
    DailyTrendsView,
    CrimesBySeverityView,
    RecentCrimesView,
    AlertsView,
    OfficerStatsView,
    CategoryDistrictView,
)

urlpatterns = [
    # Main overview
    path('overview/',           DashboardOverviewView.as_view(),  name='dashboard-overview'),

    # Crime breakdowns
    path('crimes-by-category/', CrimesByCategoryView.as_view(),  name='crimes-by-category'),
    path('crimes-by-severity/', CrimesBySeverityView.as_view(),  name='crimes-by-severity'),
    path('category-district/',  CategoryDistrictView.as_view(),  name='category-district'),

    # Hotspots
    path('hotspots/',           CrimeHotspotsView.as_view(),     name='crime-hotspots'),

    # Trends
    path('trends/monthly/',     MonthlyTrendsView.as_view(),     name='monthly-trends'),
    path('trends/daily/',       DailyTrendsView.as_view(),       name='daily-trends'),

    # Live feed
    path('recent-crimes/',      RecentCrimesView.as_view(),      name='recent-crimes'),
    path('alerts/',             AlertsView.as_view(),            name='alerts'),

    # Officer personal stats
    path('my-stats/',           OfficerStatsView.as_view(),      name='my-stats'),
]