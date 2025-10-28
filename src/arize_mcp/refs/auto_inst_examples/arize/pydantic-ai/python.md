### Install

```bash
pip install openinference-instrumentation-pydantic-ai pydantic-ai opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-api
```

### Setup tracing

```python
import os
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry.sdk.resources import Resource

# Set the Space and API keys as headers for authentication
headers = f"space_id={os.environ['ARIZE_SPACE_ID']},api_key={os.environ['ARIZE_API_KEY']}"
os.environ['OTEL_EXPORTER_OTLP_TRACES_HEADERS'] = headers

# Set resource attributes for the name and version for your application
trace_attributes = {
  "model_id": "your project name", # This is how your project will show up in Arize AX
  "model_version": "v1", # You can filter your spans by project version in Arize AX
}

# Set the tracer provider
tracer_provider = trace_sdk.TracerProvider(
  resource=Resource(attributes=trace_attributes)
)
tracer_provider.add_span_processor(OpenInferenceSpanProcessor())
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter("https://otlp.arize.com/v1")))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)
```

### Run Pydantic AI

```python
from pydantic import BaseModel
from pydantic_ai import Agent

# For example - could be any LLM provider
from pydantic_ai.models.openai import OpenAIModel

# Set your API key (depends on LLM provider)
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class LocationModel(BaseModel):
    city: str
    country: str

model = OpenAIModel("gpt-4", provider='openai')
agent = Agent(model, output_type=LocationModel, instrument=True)

result = agent.run_sync("The windy city in the US of A.")
print(result)
```