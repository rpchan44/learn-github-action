import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from myutils import load_config

import os

# Server configuration
bind = "0.0.0.0:80"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging configuration
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Custom logging format
log_format = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S %z'

# Set up logging with custom format
logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
logger = logging.getLogger(__name__)

# Function to configure and return the tracer provider
def create_tracer_provider(service_name: str) -> TracerProvider:
    try:
        # Create and configure the resource (service metadata)
        resource = Resource.create(attributes={"service.name": service_name})
        # Set up the tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        return tracer_provider
    except Exception as e:
        logger.error("Failed to create tracer provider: %s", e)
        raise

# Function to configure the OTLP exporter and add the span processor
def configure_span_exporter(tracer_provider: TracerProvider, endpoint: str, secure: bool = False) -> None:
    try:
        # Decide whether to use secure communication (HTTPS)
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            insecure=not secure  # If secure is False, it defaults to 'insecure=True'
        )
        # Configure the span processor (this will export the spans in batches)
        span_processor = BatchSpanProcessor(exporter)
        tracer_provider.add_span_processor(span_processor)
        logger.info("OTLP exporter configured with endpoint: %s", endpoint)
    except Exception as e:
        logger.error("Failed to configure span exporter: %s", e)
        raise

# Post-fork worker setup (this gets called after each worker is forked in Gunicorn)
def post_fork(server, worker):
    try:
        logger.info("Booting worker with pid: %s", worker.pid)
        config_path = os.getenv('CONFIG_FILE_PATH', '/app/config.properties')
        config = load_config(config_path)
        linkerd = config.get('linkerd', 'linkerd')

        if linkerd == 'True':
           # Set up the OpenTelemetry tracer provider and exporter
           service_name = "dev-webapp"
           tracer_provider = create_tracer_provider(service_name)
           # Configure the exporter (change endpoint as necessary for your OTLP collector)
           otlp_endpoint = "http://collector.linkerd-jaeger:4317"  # Change to "https" if using secure transport
           configure_span_exporter(tracer_provider, otlp_endpoint, secure=False)  # Set secure=True if using HTTPS
        else:
           logger.info("Service mesh is disabled")

    except Exception as e:
        logger.error("Error in post_fork: %s", e)
        raise

