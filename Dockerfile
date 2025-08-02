# Dockerfile

# Stage 1: Use an official Python runtime as a parent image
# Using -slim is a good practice for smaller image sizes.
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Set environment variables
# 1. Prevents Python from writing .pyc files.
# 2. Prevents Python from buffering stdout and stderr.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed (e.g., for certain DB drivers)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Python dependencies
# First, copy only the requirements file to leverage Docker's layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
# This assumes your FastAPI code is in a directory named 'app'
COPY ./app ./app

# Expose the port the app runs on
# Your script uses port 8000, so we'll expose that.
EXPOSE 8000

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app
USER app

# Command to run the application
# We run uvicorn directly. This is the production way.
# --host 0.0.0.0 is crucial to allow connections from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]