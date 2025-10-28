### Install

```bash
pip install openinference-instrumentation-openai-agents openai-agents arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Setup

```python
# Import open-telemetry dependencies
from arize.otel import register

# Setup OTel via our convenience function
tracer_provider = register(
    space_id = "your-space-id",    # in app space settings page
    api_key = "your-api-key",      # in app space settings page
    project_name="agents"          # As used in the example, or your preferred project name
)

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.openai import OpenAIInstrumentor

# Finish automatic instrumentation
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
```