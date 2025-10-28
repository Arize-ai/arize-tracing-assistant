# Manual Instrumentation Example: Sending Traces to Phoenix

Demonstrates how to manually add OpenTelemetry + OpenInference tracing to a Python app and export spans to a **Phoenix** backend running locally.

---

## 0. Prerequisites

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http openinference-semconv openinference-instrumentation
# Phoenix (local):
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

---

## 1. Imports

```python
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk import trace as trace_sdk
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry import trace as trace_api
import json
from openinference.instrumentation import using_attributes
from opentelemetry.trace import Status, StatusCode
from openinference.semconv.resource import ResourceAttributes
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
```

---

## 2. TracerProvider Registration (Phoenix)

```python
# Set up resource attributes for Phoenix project name
trace_attributes = {
    ResourceAttributes.PROJECT_NAME: "manual-traces",
}

# Create a TracerProvider with the resource attributes
provider = trace_sdk.TracerProvider(resource=Resource(attributes=trace_attributes))

# Configure the OTLP HTTP exporter to send traces to Phoenix (local)
exporter = OTLPSpanExporter(endpoint="http://localhost:6006/v1/traces")

# Add a simple span processor to the provider
provider.add_span_processor(SimpleSpanProcessor(exporter))

# Register the provider globally
trace_api.set_tracer_provider(provider)
```

---

## 3. Tracer and Span Creation

```python
# Get a tracer instance for this module
tracer = trace_api.get_tracer(__name__)

# Use OpenInference's using_attributes context manager to attach session/user info
with using_attributes(
    session_id="123456",
    user_id="31415",
):
    # Start a parent span (Agent)
    with tracer.start_as_current_span(
        name="Parent span",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
            SpanAttributes.INPUT_VALUE: "Foo faa",
        },
    ) as agent_span:
        # Child span 1: Embedding
        with tracer.start_as_current_span(
            name="Child span 1",
            attributes={
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.EMBEDDING.value,
                SpanAttributes.INPUT_VALUE: "Some embedding input",
            },
        ) as child_span:
            # Simulate work and set output/metadata
            child_span.set_attribute(
                SpanAttributes.OUTPUT_VALUE, "Some embedding output"
            )
            metadata_json_str = json.dumps({"some_metadata": True})
            child_span.set_attribute(SpanAttributes.METADATA, metadata_json_str)
            # Child span 2: LLM
            with tracer.start_as_current_span(
                name="Child span 2",
                attributes={
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.LLM.value,
                    SpanAttributes.INPUT_VALUE: "Some LLM input",
                },
            ) as child_span:
                output = "Some LLM output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
            # Child span 3: Tool
            with tracer.start_as_current_span(
                name="Child span 3",
                attributes={
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
                    SpanAttributes.INPUT_VALUE: "Some tool input",
                },
            ) as child_span:
                output = "Some tool output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
        # Child span 4: Chain
        with tracer.start_as_current_span(
            name="Child span 4",
            attributes={
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.CHAIN.value,
                SpanAttributes.INPUT_VALUE: "Some chain input",
            },
        ) as child_span:
            try:
                print("CallingLM")
                output = "Some LLM output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
            except Exception as error:
                agent_span.record_exception(error)
                agent_span.set_status(Status(StatusCode.ERROR))
            else:
                agent_span.set_status(Status(StatusCode.OK))
```

---

# END EXAMPLE 