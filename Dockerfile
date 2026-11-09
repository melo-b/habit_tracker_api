# Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# Bring in uv (pinned) from the official image
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

# Prevent Python from writing .pyc files and force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Run installed tools straight from the project virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Set the working directory inside the container
WORKDIR /app

# Install dependencies first (cached unless pyproject.toml / uv.lock change)
COPY pyproject.toml uv.lock .python-version /app/
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for external access
EXPOSE 8000

# Run migrations, attempt to create superuser, and start the Gunicorn server
CMD ["sh", "-c", "python manage.py migrate && python manage.py createsuperuser --noinput || true && gunicorn core.wsgi --bind 0.0.0.0:8000"]
