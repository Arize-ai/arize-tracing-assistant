# Manual Instrumentation Example: Sending Traces to Arize

Demonstrates how to manually add OpenTelemetry + OpenInference tracing to a Python app and export spans to **Arize**.

---

## 0. Prerequisites

```bash
pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc openinference-semconv openinference-instrumentation
# Arize credentials (replace with your values):
export ARIZE_SPACE_KEY="<your-space-key>"
export ARIZE_API_KEY="<your-api-key>"
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
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGrpc,
)
```

---

## 2. TracerProvider Registration (Arize)

```python
# Set up Arize credentials and endpoint
ARIZE_SPACE_KEY = "ARIZE_SPACE_KEY"
ARIZE_API_KEY = "ARIZE_API_KEY"
ARIZE_MODEL_NAME = "my-manually-instrumented-project"
ARIZE_ENDPOINT = "otlp.arize.com"

# Create a TracerProvider with Arize model info as resource attributes
provider = trace_sdk.TracerProvider(
    resource=Resource(
        attributes={
            "model_id": ARIZE_MODEL_NAME,
            "model_version": "v1",
        }
    )
)

# Configure the OTLP gRPC exporter to send traces to Arize
exporter = OTLPSpanExporterGrpc(
    endpoint=ARIZE_ENDPOINT,
    headers={
        "space_key": ARIZE_SPACE_KEY,
        "api_key": ARIZE_API_KEY,
    },
)

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