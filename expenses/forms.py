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

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_name(self):
        name = self.cleaned_data["name"]

        categories = Category.objects.filter(
            owner=self.user,
            name=name,
        )

        if self.instance.pk:
            categories = categories.exclude(pk=self.instance.pk)

        if self.user is not None and categories.exists():
            raise forms.ValidationError(
                "Категорія з такою назвою вже існує"
            )

        return name
