### Install

```bash
pip install openinference-instrumentation-pydantic-ai pydantic-ai opentelemetry-sdk opentelemetry-exporter-otlp opentelemetry-api
```

### Setup tracing

```python
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Set up the tracer provider
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)

# Add the OpenInference span processor
endpoint = f"{os.environ['PHOENIX_COLLECTOR_ENDPOINT']}/v1/traces"

# If you are using a local instance without auth, ignore these headers
headers = {"Authorization": f"Bearer {os.environ['PHOENIX_API_KEY']}"}
exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)

tracer_provider.add_span_processor(OpenInferenceSpanProcessor())
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
```

### Run Pydantic AI

```python
from pydantic import BaseModel
from pydantic_ai import Agent

# For example - may be any LLM provider offered by pydanticai
from pydantic_ai.models.openai import OpenAIModel 
import nest_asyncio

# Set your api key (depends on the LLM provider)
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class LocationModel(BaseModel):
    city: str
    country: str

model = OpenAIModel("gpt-4", provider='openai')
agent = Agent(model, output_type=LocationModel, instrument=True)

result = agent.run_sync("The windy city in the US of A.")
print(result)
```
