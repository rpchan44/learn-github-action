# Use an official Python runtime as a parent image
FROM python:3.9-slim

ARG ENVIRONMENT=production

# Set environment variables to disable Python bytecode generation and enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
    
# Set the working directory in the container
WORKDIR /app
ENV FLASK_RUN_PORT=80
ENV FLASK_RUN_HOST=0.0.0.0

# Copy the config file into the container at build time
COPY config.${ENVIRONMENT}.properties /app/config.${ENVIRONMENT}.properties
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY templates /app/templates


# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mysql-connector-python
RUN pip install redis

# Set environment variable based on the properties file
# (You may want to modify app.py to read directly from the file)
ENV CONFIG_FILE_PATH=/app/config.${ENVIRONMENT}.properties

# Command to run the application using Gunicorn for production
EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]

