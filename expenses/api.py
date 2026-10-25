from rest_framework import permissions, viewsets

from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Expense.objects.select_related("category")
            .filter(owner=self.request.user)
            .order_by("-spent_at", "-id")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
