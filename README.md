# Django Expense Tracker

A personal expense tracker built with Django. Users can manage their expenses through a web interface and basic JSON endpoints.

**Status:** In active development.

## Features

- User authentication using Django's built-in authentication system.
- Create, view, edit, and delete expenses.
- Per-user data isolation: users can access only their own expenses.
- Total expense calculation.
- Expenses ordered by date.
- Validation of positive amounts at the form and database levels.
- JSON endpoints for listing and creating expenses.
- Automated tests.

## Tech Stack

- Python
- Django
- SQLite
- Django Templates
- HTML

The JSON endpoints use Django views and `JsonResponse`, without Django REST Framework.

## Local Setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/luts26/django-expense-tracker.git
cd django-expense-tracker
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Create a user:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open the local address shown in the terminal and sign in using
the account you created.

## Tests

Run the test suite:

```bash
python manage.py test
```

Run Django's system checks:

```bash
python manage.py check
```

Check for model changes without migrations:

```bash
python manage.py makemigrations --check --dry-run
```

## Project Structure

```text
config/                 Django settings and root URL configuration
expenses/
    models.py           Expense and category models
    forms.py            Expense form and validation
    views.py            Web views and JSON endpoints
    urls.py             Expense routes
    tests.py            Automated tests
    migrations/         Database migrations
    templates/          Expense pages
templates/
    registration/       Login template
manage.py               Django management commands
requirements.txt        Python dependencies
```

## Data and Access Control

Each expense belongs to a user. List, edit, and delete operations
filter records by the authenticated owner.

Amounts use `DecimalField`. Validation and a database constraint
require an amount of at least `0.01`.

The JSON endpoints use session authentication and Django's CSRF
protection. They do not currently provide token-based authentication.

## Development Notes

The default configuration is intended for local development,
using SQLite and `DEBUG=True`.

`DJANGO_SECRET_KEY` can be supplied through an environment variable.
The fallback key is for local development only.

Do not commit local databases, virtual environments, or secrets.
Production deployment requires separate security and hosting
configuration.

## Planned Improvements

- Connect categories to expenses and add category management.
- Add filtering and pagination.
- Improve the user interface.
- Add reporting and export functionality.