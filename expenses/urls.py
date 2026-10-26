from rest_framework.routers import SimpleRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path

from . import views
from .api import ExpenseViewSet

app_name = "expenses"
router = SimpleRouter()

router.register("api/expenses", ExpenseViewSet, basename="api-expense")

urlpatterns = [
    path("api/token/", obtain_auth_token, name="api-token"),
    path("api/", views.expense_api_list, name="api-list"),
    path("categories/", views.category_list, name="category-list"),
    path("categories/new/", views.category_create, name="category-create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category-update"),
    path("report/", views.expense_report, name="report"),
    path("export.csv", views.expense_export_csv, name="export-csv"),
    path("new/", views.expense_create, name="create"),
    path("<int:pk>/edit/", views.expense_update, name="update"),
    path("<int:pk>/delete/", views.expense_delete, name="delete"),
    path("", views.expense_list, name="list"),
]

urlpatterns += router.urls
