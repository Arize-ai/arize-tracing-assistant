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

# Sending traces to Arize
ARIZE_SPACE_KEY = "ARIZE_SPACE_KEY"
ARIZE_API_KEY = "ARIZE_API_KEY"
ARIZE_MODEL_NAME = "my-manually-instrumented-project"
ARIZE_ENDPOINT = "otlp.arize.com"

provider = trace_sdk.TracerProvider(
    resource=Resource(
        attributes={
            "model_id": ARIZE_MODEL_NAME,
            "model_version": "v1",
        }
    )
)

exporter = OTLPSpanExporterGrpc(
    endpoint=ARIZE_ENDPOINT,
    headers={
        "space_key": ARIZE_SPACE_KEY,
        "api_key": ARIZE_API_KEY,
    },
)


provider.add_span_processor(SimpleSpanProcessor(exporter))

trace_api.set_tracer_provider(provider)


tracer = trace_api.get_tracer(__name__)

with using_attributes(
    session_id="123456",
    user_id="31415",
):
    with tracer.start_as_current_span(
        name="Parent span",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
            SpanAttributes.INPUT_VALUE: "Foo faa",
        },
    ) as agent_span:
        with tracer.start_as_current_span(
            name="Child span 1",
            attributes={
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.EMBEDDING.value,
                SpanAttributes.INPUT_VALUE: "Some embedding input",
            },
        ) as child_span:
            # perform some work
            child_span.set_attribute(
                SpanAttributes.OUTPUT_VALUE, "Some embedding output"
            )
            metadata_json_str = json.dumps({"some_metadata": True})
            child_span.set_attribute(SpanAttributes.METADATA, metadata_json_str)
            with tracer.start_as_current_span(
                name="Child span 2",
                attributes={
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.LLM.value,
                    SpanAttributes.INPUT_VALUE: "Some LLM input",
                },
            ) as child_span:
                # perform more work
                output = "Some LLM output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
            with tracer.start_as_current_span(
                name="Child span 3",
                attributes={
                    SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.TOOL.value,
                    SpanAttributes.INPUT_VALUE: "Some tool input",
                },
            ) as child_span:
                # perform more work
                output = "Some tool output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)
        with tracer.start_as_current_span(
            name="Child span 4",
            attributes={
                SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.CHAIN.value,
                SpanAttributes.INPUT_VALUE: "Some chain input",
            },
        ) as child_span:
            # perform more work
            try:
                print("CallingLM")
                output = "Some LLM output"
                child_span.set_attribute(SpanAttributes.OUTPUT_VALUE, output)

            except Exception as error:
                agent_span.record_exception(error)
                agent_span.set_status(Status(StatusCode.ERROR))
            else:
                # child_span.set_output(response)
                agent_span.set_status(Status(StatusCode.OK))
