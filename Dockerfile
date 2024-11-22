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

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /app/wheels /wheels

COPY . /app/
RUN pip install --no-index --find-links=/wheels -r /app/requirements.txt

ENV CONFIG_FILE_PATH=/app/config.${ENVIRONMENT}.properties
WORKDIR /app

# Expose port and define the command for Gunicorn
EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]

