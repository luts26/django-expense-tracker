from rest_framework import serializers

from .models import Category, Expense

class OwnCategoryField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return Category.objects.none()
        return Category.objects.filter(owner=request.user)

class ExpenseSerializer(serializers.ModelSerializer):
    category = OwnCategoryField(required=False, allow_null=True)
    
    class Meta:
        model = Expense
        fields = [
            "id",
            "category",
            "amount",
            "description",
            "spent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
