# Stage 1: Build Stage
FROM python:3.9-slim as builder

# Set environment variables to disable Python bytecode generation and enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Declare build argument for environment
ARG ENVIRONMENT=production

# Copy the corresponding config file based on the environment argument
COPY config.${ENVIRONMENT}.properties /app/config.${ENVIRONMENT}.properties
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY templates /app/templates

# Install build dependencies and application dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mysql-connector-python
RUN pip install redis

# Stage 2: Final Stage (runtime image)
FROM python:3.9-slim

# Set environment variables for the runtime environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_RUN_PORT=80 \
    FLASK_RUN_HOST=0.0.0.0 \
    CONFIG_FILE_PATH=/app/config.${ENVIRONMENT}.properties

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage (application code and dependencies)
COPY --from=builder /app /app

# Expose the port the app will run on
EXPOSE 80

# Command to run the application using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]

