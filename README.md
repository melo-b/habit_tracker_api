# Habit Tracker API

![CI Status](https://github.com/melo-b/habit_tracker_api/actions/workflows/django-test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.x-092E20.svg)
![DRF](https://img.shields.io/badge/DRF-red.svg)

A robust, production-ready REST API for tracking daily habits. Built with Django and Django REST Framework, this project emphasizes secure authentication, relational database design, automated testing, and CI/CD best practices.

## 🚀 Key Features

*   **Role-Based Access Control (RBAC):** Custom user model enforcing Admin, Staff, and User permissions. Users can only access their own data.
*   **JWT Authentication:** Secure login and session management using JSON Web Tokens.
*   **Relational Data Integrity:** Enforces database-level constraints (e.g., preventing duplicate daily logs for the same habit).
*   **Automated Documentation:** Self-generating OpenAPI 3.0 schema exposed via an interactive Swagger UI.
*   **Continuous Integration:** Automated testing pipeline via GitHub Actions to ensure code reliability on every push.

## 🛠️ Tech Stack

*   **Core Framework:** Python 3.12, Django 5.x, Django REST Framework (DRF)
*   **Database:** PostgreSQL
*   **Authentication:** SimpleJWT (JSON Web Tokens)
*   **Testing:** Pytest, Pytest-Django
*   **API Documentation:** DRF-Spectacular (Swagger UI)
*   **CI/CD:** GitHub Actions
*   **Server:** Gunicorn

## 💻 Local Setup

If you want to run this API locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/habit_tracker_api.git](https://github.com/YOUR_USERNAME/habit_tracker_api.git)
   cd habit_tracker_api


2. **Create and activate a virtual environment:**
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate


3. **Install dependencies:**
    pip install -r requirements.txt


4. **Set up PostgreSQL Database:**
    Ensure PostgreSQL is running locally. Create a database named `habit_tracker_db` with the username `postgres` and your configured password.

5. **Run migrations:**
    ```bash
   python manage.py migrate

6. **Start Development Server:**
    python manage.py runserver


## 📖 API Documentation

Once the server is running, you can interact with the API without writing any frontend code. Navigate to the automatically generated Swagger UI:

*   **Swagger UI:** `http://localhost:8000/api/docs/`
*   **OpenAPI Schema:** `http://localhost:8000/api/schema/`

## 🧪 Testing

This project utilizes `pytest` to ensure business logic and security permissions remain intact. The test suite uses a temporary database, ensuring your local data is never affected.

To run the test suite:
```bash
pytest


