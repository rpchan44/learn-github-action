# Stage 1: Builder stage
FROM python:3.11-alpine AS builder
ARG ENVIRONMENT=production
# Install dependencies to build wheels
RUN apk add --update \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers

# Create the /app directory and copy the files
RUN mkdir /app
COPY . /app

# Install wheel and generate wheels for Flask and other dependencies
WORKDIR /app
RUN pip install wheel
RUN pip wheel -r requirements.txt --wheel-dir=/app/wheels

# Stage 2: Final image
FROM python:3.11-alpine

ARG ENVIRONMENT=production

COPY --from=builder /app/wheels /wheels

COPY . /app/
RUN pip install --no-index --find-links=/wheels -r /app/requirements.txt
RUN opentelemetry-bootstrap --action=install
ENV CONFIG_FILE_PATH=/app/config.${ENVIRONMENT}.properties
EXPOSE 80
WORKDIR /app
# Expose port and define the command for Gunicorn
EXPOSE 80
# Run the application using OpenTelemetry instrumentation
CMD ["gunicorn", "app:app", "-c", "gunicorn_config.py"]
