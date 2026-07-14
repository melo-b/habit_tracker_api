# Habit Tracker API

![CI Status](https://github.com/melo-b/habit_tracker_api/actions/workflows/django-test.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Django](https://img.shields.io/badge/Django-5.x-092E20.svg)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)

A robust, production-ready REST API for tracking daily habits. Built with Django and Django REST Framework, this project emphasizes secure authentication, relational database design, automated testing, and CI/CD best practices.

**🟢 [View the Live API Documentation (Swagger UI)](https://habit-tracker-api-wd5j.onrender.com/api/docs/)**

## 🏗️ The Engineering Approach
Transitioning into software development from a background in mechanical engineering and the testing, inspection, and certification (TIC) industry, I approach backend architecture with a focus on system reliability and rigorous quality assurance. This API wasn't just built to work locally; it was designed with production-grade standards: 
* **Isolated Infrastructure:** Containerized via Docker to eliminate environment drift.
* **Proactive Monitoring:** Integrated with the Sentry SDK to catch unhandled exceptions in production before they impact users.
* **Automated Quality Control:** Protected by a strict Pytest suite and GitHub Actions CI/CD pipeline that blocks failing code from reaching deployment.

## 🚀 Key Features
* **Role-Based Access Control (RBAC):** Custom user model enforcing Admin, Staff, and User permissions. Users can only access their own data.
* **JWT Authentication:** Secure stateless session management using JSON Web Tokens.
* **Relational Data Integrity:** Enforces database-level constraints (e.g., preventing duplicate daily logs or logging habits in the future).
* **Automated Documentation:** Self-generating OpenAPI 3.0 schema exposed via an interactive Swagger UI.

## 🗄️ Data Architecture
The database is structured in PostgreSQL using the following core relational models:
* **User:** Handles authentication and permissions.
* **Habit:** Stores the target habit (Foreign Key to `User`).
* **HabitLog:** Tracks daily completions. Features a unique constraint on `(habit, date)` to prevent duplicate entries, and custom validation to prevent logging future dates.

## 🛠️ Tech Stack
* **Core Framework:** Python 3.12, Django 5.x, Django REST Framework (DRF)
* **Database & Caching:** PostgreSQL
* **Infrastructure:** Docker, Docker Compose, Gunicorn
* **DevOps & Monitoring:** GitHub Actions (CI/CD), Sentry SDK, Render (Cloud Hosting)
* **Testing:** Pytest, Pytest-Django

## 💻 Local Setup (Dockerized)

This application is fully containerized. You do not need to install Python or PostgreSQL on your local machine to run it.

1. **Clone the repository:**
```bash
   git clone https://github.com/melo-b/habit_tracker_api.git
   cd habit_tracker_api
```


2. **Configure Environment Variables:**
    Create a .env file in the root directory and add the following required variables:
        ```.env
        SECRET_KEY=your_development_secret_key
        DEBUG=True
        DB_NAME=habit_tracker_db
        DB_USER=postgres
        DB_PASSWORD=your_postgres_password
        DB_HOST=db
        ```
        


3. **Build and Start the Containers:**
    ```bash
    docker compose up --build
    ```


4. **Run Migrations & Create Superuser (In a new terminal tab):**
    ```bash
    docker compose exec web python manage.py migrate
    docker compose exec web python manage.py createsuperuser
    ```




## 📖 API Documentation

Once the Docker containers are running, navigate to the automatically generated Swagger UI to interact with the endpoints:

Swagger UI: http://localhost:8000/api/docs/

## 🧪 Testing

The test suite uses an isolated temporary database, ensuring your local data is never affected. Run the test suite directly inside the Docker container:

```bash
docker compose exec web pytest
```



## 🗺️ Roadmap
Future planned upgrades for this architecture:

* Implement Redis for API response caching.

* Integrate Celery and Redis to handle asynchronous email reminders for uncompleted habits.


## 🤝 Let's Connect
Rommelo Balandra 
* LinkedIn: [Profile](https://www.linkedin.com/in/rommelobalandra/)
