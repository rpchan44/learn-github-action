# Use an official Python runtime as a parent image
FROM python:3.9-slim

ARG ENVIRONMENT=production
# Set the working directory in the container
WORKDIR /app
ENV FLASK_RUN_PORT=80
ENV FLASK_RUN_HOST=0.0.0.0

# Copy the config file into the container at build time
COPY config.${ENVIRONMENT}.properties /app/config.${ENVIRONMENT}.properties
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mysql-connector-python
RUN pip install redis

EXPOSE 80

# Set environment variable based on the properties file
# (You may want to modify app.py to read directly from the file)
ENV FLASK_APP=app.py
ENV CONFIG_FILE_PATH=/app/config.${ENVIRONMENT}.properties

# Run the Flask app when the container starts
CMD ["flask", "run"]
