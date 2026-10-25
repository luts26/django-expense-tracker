from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Expense.objects.select_related("category")
            .filter(owner=self.request.user)
            .order_by("-spent_at", "-id")
        )

        category = self.request.query_params.get("category")

        if category is not None:
            if not category.isdecimal():
                raise ValidationError({"category": "Must be an integer id"})
            queryset = queryset.filter(category_id=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
