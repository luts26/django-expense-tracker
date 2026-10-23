from django.conf import settings
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class Category(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_categories",
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_category_name_per_owner",
            ),
        ]

    def __str__(self):
        return self.name

class Expense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    description = models.CharField(max_length=255)
    spent_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=Decimal("0.01")),
                name="expense_amount_gte_001",
            ),
        ]

    def __str__(self):
        return f"{self.description}: {self.amount}"
