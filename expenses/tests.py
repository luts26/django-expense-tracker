from datetime import date
from decimal import Decimal
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError, transaction

from .models import Expense

class ExpenseModelTest(TestCase):
    def test_string_representation(self):
        user = get_user_model().objects.create_user(username="tester")
        expense = Expense.objects.create(
            owner=user,
            amount=Decimal("12.51"),
            description="Кава",
            spent_at=date(2026, 10, 17),
        )

        self.assertEqual(str(expense), "Кава: 12.51")

    def test_database_rejects_non_positive_amount(self):
        user = get_user_model().objects.create_user(username="constraint-user")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Expense.objects.create(
                    owner=user,
                    amount=Decimal("0.00"),
                    description="Нульова витрата",
                    spent_at=date(2026, 10, 21),
                )

class ExpenseListViewTest(TestCase):
    def test_requires_authentication(self):
        list_url = reverse("expenses:list")
        login_url = reverse("login")

        response = self.client.get(list_url)

        self.assertRedirects(
            response,
            f"{login_url}?next={list_url}",
        )

    def test_shows_only_current_user_expenses(self):
        user_model = get_user_model()
        current_user = user_model.objects.create_user(username="current")
        other_user = user_model.objects.create_user(username="other")

        Expense.objects.create(
            owner=current_user,
            amount=Decimal("10.00"),
            description="Моя витрата",
            spent_at=date(2026, 10, 20),
        )
        Expense.objects.create(
            owner=other_user,
            amount=Decimal("20.00"),
            description="Інша витрата",
            spent_at=date(2026, 10, 20),
        )

        self.client.force_login(current_user)
        response = self.client.get(reverse("expenses:list"))

        self.assertContains(response, "Моя витрата")
        self.assertNotContains(response, "Інша витрата")
        self.assertEqual(
            response.context["total"],
            Decimal("10.00"),
        )

class ExpenseCreateViewTest(TestCase):
    def test_assigns_authenticated_user_as_owner(self):
        user = get_user_model().objects.create_user(username="creator")
        self.client.force_login(user)

        response = self.client.post(
            reverse("expenses:create"),
            {
                "amount": "15.75",
                "description": "Транспорт",
                "spent_at": "2026-10-20",
            },
        )

        self.assertRedirects(response, reverse("expenses:list"))

        expense = Expense.objects.get()
        self.assertEqual(expense.owner, user)
        self.assertEqual(expense.amount, Decimal("15.75"))
        self.assertEqual(expense.description, "Транспорт")

class ExpenseApiListTest(TestCase):
    def test_returns_only_current_users_expenses(self):
        user_model = get_user_model()
        current_user = user_model.objects.create_user(username="api-user")
        other_user = user_model.objects.create_user(username="other-api-user")

        Expense.objects.create(
            owner=current_user,
            amount=Decimal("35.50"),
            description="Автобус",
            spent_at=date(2026, 10, 21),
        )
        Expense.objects.create(
            owner=other_user,
            amount=Decimal("99.00"),
            description="Other record",
            spent_at=date(2026, 10, 21),
        )

        self.client.force_login(current_user)
        response = self.client.get(reverse("expenses:api-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "expenses": [
                    {
                        "id": 1,
                        "amount": "35.50",
                        "description": "Автобус",
                        "spent_at": "2026-10-21",
                    },
                ],
            },
        )

    def test_rejects_put(self):
        user = get_user_model().objects.create_user(username="api-putter")
        self.client.force_login(user)

        response = self.client.put(reverse("expenses:api-list"))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.headers["Allow"], "GET, POST")

    def test_creates_expense_from_json(self):
        user = get_user_model().objects.create_user(username="api-creator")
        self.client.force_login(user)

        response = self.client.post(
            reverse("expenses:api-list"),
            data=json.dumps(
                {
                    "amount": "118.00",
                    "description": "Taxi",
                    "spent_at": "2026-10-21",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        expense = Expense.objects.get()
        self.assertEqual(expense.owner, user)
        self.assertEqual(expense.amount, Decimal("118.00"))

    def test_rejects_invalid_expense_data(self):
        user = get_user_model().objects.create_user(username="api-invalid")
        self.client.force_login(user)

        response = self.client.post(
            reverse("expenses:api-list"),
            data=json.dumps(
                {
                    "description": "Без суми",
                    "spent_at": "2026-10-21",
                }
            ),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json()["errors"])
        self.assertFalse(Expense.objects.exists())

    def test_rejects_non_positive_amount(self):
        user = get_user_model().objects.create_user(username="api-negative")
        self.client.force_login(user)

        response = self.client.post(
            reverse("expenses:api-list"),
            data=json.dumps(
                {
                    "amount": "-1.00",
                    "description": "Not valid amount",
                    "spent_at": "2026-10-21",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("amount", response.json()["errors"])
        self.assertFalse(Expense.objects.exists())

class ExpenseUpdateViewTest(TestCase):
    def test_returns_404_for_another_user_expense(self):
        user_model = get_user_model()
        current_user = user_model.objects.create_user(username="editor")
        other_user = user_model.objects.create_user(username="other-owner")

        expense = Expense.objects.create(
            owner=other_user,
            amount=Decimal("30.00"),
            description="Other spend",
            spent_at=date(2026, 10, 22),
        )

        self.client.force_login(current_user)
        response = self.client.get(
            reverse("expenses:update", args=[expense.pk])
        )

        self.assertEqual(response.status_code, 404)

class ExpenseDeleteViewTest(TestCase):
    def test_deletes_own_expense(self):
        user = get_user_model().objects.create_user(username="deleter")
        expense = Expense.objects.create(
            owner=user,
            amount=Decimal("11.00"),
            description="Delete record",
            spent_at=date(2026, 10, 22),
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("expenses:delete", args=[expense.pk])
        )

        self.assertRedirects(response, reverse("expenses:list"))
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_does_not_delete_via_get(self):
        user = get_user_model().objects.create_user(username="get-deleter")
        expense = Expense.objects.create(
            owner=user,
            amount=Decimal("9.00"),
            description="Save me",
            spent_at=date(2026, 10, 22),
        )
        self.client.force_login(user)

        response = self.client.get(
            reverse("expenses:delete", args=[expense.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Expense.objects.filter(pk=expense.pk).exists())
