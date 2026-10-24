from decimal import Decimal
import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum


from .forms import CategoryForm, ExpenseForm
from .models import Category, Expense

def _expense_to_dict(expense):
    category = None

    if expense.category is not None:
        category = {
            "id": expense.category.id,
            "name": expense.category.name,
        }

    return {
        "id": expense.id,
        "amount": expense.amount,
        "description": expense.description,
        "spent_at": expense.spent_at,
        "category": category,
    }

@login_required
def category_list(request):
    categories = Category.objects.filter(
        owner=request.user,
    )

    return render(
        request,
        "expenses/category_list.html",
        {
            "categories": categories
        }
    )

@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, user=request.user)

        if form.is_valid():
            category = form.save(commit=False)
            category.owner = request.user
            category.save()

            return redirect("expenses:category-list")
    else:
        form = CategoryForm(user=request.user)

    return render(
        request,
        "expenses/category_form.html",
        {
            "form": form,
            "title": "New category",
        },
    )

@login_required
def category_update(request, pk):
    category = get_object_or_404(
        Category,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        form = CategoryForm(
            request.POST,
            instance=category,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("expenses:category-list")
    else:
        form = CategoryForm(
            instance=category,
            user=request.user,
        )

    return render(
        request,
        "expenses/category_form.html",
        {
            "form": form,
            "title": "Редагувати категорію"
        }
    )

@login_required
def expense_list(request):
    expenses = Expense.objects.select_related("category").filter(
        owner=request.user,
    ).order_by("-spent_at", "-id")

    total = expenses.aggregate(total=Sum("amount"))["total"]
    total = total or Decimal("0.00")

    return render(
        request,
        "expenses/expense_list.html",
        {
            "expenses": expenses,
            "total": total,
        },
    )

@login_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, user=request.user)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.owner = request.user
            expense.save()

            return redirect("expenses:list")
    else:
        form = ExpenseForm(user=request.user)

    return render(
        request,
        "expenses/expense_form.html",
        {
            "form": form,
            "title": "Нова витрата"
        },
    )

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            instance=expense,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("expenses:list")
    else:
        form = ExpenseForm(
            instance=expense,
            user=request.user,
        )

    return render(
        request,
        "expenses/expense_form.html",
        {
            "form": form,
            "title": "Edit expense"
        },
    )

@login_required
@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(
        Expense,
        pk=pk,
        owner=request.user,
    )
    expense.delete()

    return redirect("expenses:list")

@login_required
@require_http_methods(["GET", "POST"])
def expense_api_list(request):
    if request.method == "GET":
        expenses = Expense.objects.select_related("category").filter(
            owner=request.user
        ).order_by("-spent_at", "-id")

        data = [_expense_to_dict(expense) for expense in expenses]

        return JsonResponse({"expenses": data})

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"errors": {"body": ["Invalid JSON."]}},
            status=400,
        )

    form = ExpenseForm(data, user=request.user)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    expense = form.save(commit=False)
    expense.owner = request.user
    expense.save()

    return JsonResponse(
        {
            "expense": _expense_to_dict(expense)
        },
        status=201,
    )
