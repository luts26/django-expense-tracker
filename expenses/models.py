from django.conf import settings
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class Expense(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
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
