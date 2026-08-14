from django.urls import path
from .views import RecordPurchaseView, UserStatsView, dashboard_view

urlpatterns = [
    path("purchases/", RecordPurchaseView.as_view()),
    path("user-stats/", UserStatsView.as_view()),
    path("dashboard/", dashboard_view, name="dashboard"),
]