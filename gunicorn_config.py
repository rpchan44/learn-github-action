from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPHTTPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

bind = "0.0.0.0:80"

# Sample Worker processes
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Sample logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
    resource = Resource.create(attributes={"service.name": "dev-webapp"})
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Use OTLP HTTP exporter
    span_processor = BatchSpanProcessor(
        OTLPHTTPSpanExporter(endpoint="http://collector.linkerd-jaeger:4318", insecure=True)
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

