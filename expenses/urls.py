from django.urls import path

from . import views

app_name = "expenses"

urlpatterns = [
    path("api/", views.expense_api_list, name="api-list"),
    path("categories/", views.category_list, name="category-list"),
    path("categories/new/", views.category_create, name="category-create"),
    path("new/", views.expense_create, name="create"),
    path("<int:pk>/edit/", views.expense_update, name="update"),
    path("<int:pk>/delete/", views.expense_delete, name="delete"),
    path("", views.expense_list, name="list"),
]
