# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the config file into the container at build time
COPY config.properties /app/config.properties
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Set environment variable based on the properties file
# (You may want to modify app.py to read directly from the file)
ENV FLASK_APP=app.py
ENV CONFIG_FILE_PATH=/app/config.properties

# Run the Flask app when the container starts
CMD ["flask", "run"]
