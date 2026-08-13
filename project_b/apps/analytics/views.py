from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import UserPurchase

class RecordPurchaseView(APIView):
    def post(self, request):
        UserPurchase.objects.create(
            user_id=request.data["user_id"],
            order_id=request.data["order_id"],
            amount=request.data["amount"],
        )
        return Response({"status": "ok"})

class UserStatsView(APIView):
    def get(self, request):
        stats = (
            UserPurchase.objects.values("user_id")
            .annotate(total_spent=Sum("amount"), orders_count=Count("id"))
        )
        return Response(list(stats))