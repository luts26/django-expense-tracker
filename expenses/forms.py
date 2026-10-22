from django import forms

from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["amount", "description", "spent_at"]
        widgets = {
            "spent_at": forms.DateInput(attrs={"type": "date"}),
        }
