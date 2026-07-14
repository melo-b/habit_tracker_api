# Use the official, lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and force stdout/stderr to be unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for external access
EXPOSE 8000

# Start the Gunicorn server
CMD ["gunicorn", "core.wsgi", "--bind", "0.0.0.0:8000"]