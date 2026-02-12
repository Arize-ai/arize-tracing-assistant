### Install

```bash
pip install strands-agents openinference-instrumentation-strands-agents opentelemetry-sdk opentelemetry-exporter-otlp
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Setup

```python
from phoenix.otel import register
from openinference.instrumentation.strands_agents import StrandsAgentsToOpenInferenceProcessor

tracer_provider = register(
  project_name="my-llm-app",
)

tracer_provider.add_span_processor(StrandsAgentsToOpenInferenceProcessor())
```

### Run your Agent

```python
from strands import Agent

agent = Agent(system_prompt="You are a helpful weather assistant.")
response = agent("What is the weather like in Seattle?")
print(response)
```
