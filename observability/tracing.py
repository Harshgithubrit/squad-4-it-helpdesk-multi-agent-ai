"""OpenTelemetry spans when enabled; safe no-op fallback otherwise."""
from functools import wraps
from contextlib import contextmanager
from config import get_settings

_settings = get_settings()
_tracer = None
if _settings.otel_enabled:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        provider = TracerProvider(resource=Resource.create({"service.name": "squad-4-it-helpdesk"}))
        trace.set_tracer_provider(provider)
        if _settings.otel_exporter == "otlp" and _settings.otel_endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=_settings.otel_endpoint)))
        else:
            from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        _tracer = trace.get_tracer("squad4.helpdesk")
    except Exception as exc:
        print(f"OpenTelemetry initialization skipped: {exc}")

def traced(name: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if _tracer is None: return fn(*args, **kwargs)
            with _tracer.start_as_current_span(name): return fn(*args, **kwargs)
        return wrapper
    return decorator

@contextmanager
def span(name: str, attributes: dict | None = None):
    if _tracer is None:
        yield
    else:
        with _tracer.start_as_current_span(name, attributes=attributes or {}): yield
