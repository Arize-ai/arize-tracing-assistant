### Install

```bash
pip install strands-agents openinference-instrumentation-strands-agents opentelemetry-sdk opentelemetry-exporter-otlp
```

### API Key Setup

```bash
export ARIZE_SPACE_ID='your-space-id'
export ARIZE_API_KEY='your-api-key'
```

### Setup

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.strands_agents import StrandsAgentsToOpenInferenceProcessor

SPACE_ID = os.environ["ARIZE_SPACE_ID"]
API_KEY = os.environ["ARIZE_API_KEY"]
ENDPOINT = "otlp.arize.com:443"

provider = TracerProvider()

# Add the OpenInference processor BEFORE the exporter
provider.add_span_processor(StrandsAgentsToOpenInferenceProcessor())

otlp_exporter = OTLPSpanExporter(
    endpoint=ENDPOINT,
    headers={
        "space_id": SPACE_ID,
        "api_key": API_KEY,
    },
)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

trace.set_tracer_provider(provider)
```

### Run your Agent

```python
from strands import Agent

agent = Agent(system_prompt="You are a helpful assistant.")
response = agent("What is the weather like in Seattle?")
print(response)
```
