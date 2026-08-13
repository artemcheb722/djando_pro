from django.urls import path
from .views import RecordPurchaseView, UserStatsView

urlpatterns = [
    path("purchases/", RecordPurchaseView.as_view()),
    path("user-stats/", UserStatsView.as_view()),
]