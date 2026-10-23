from django import forms

from .models import Category, Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "amount", "description", "spent_at"]
        widgets = {
            "spent_at": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields["category"].queryset = Category.objects.none()
        else:
            self.fields["category"].queryset = Category.objects.filter(
                owner=user,
            )
