### Install

```bash
pip install openinference-instrumentation-litellm litellm arize-otel
```

### Setup

```python
# Import open-telemetry dependencies
from arize.otel import register

# Setup OTel via our convenience function
tracer_provider = register(
    space_id = "your-space-id", # in app space settings page
    api_key = "your-api-key", # in app space settings page
    project_name = "your-project-name", # name this to whatever you would like
)

# Import the instrumentor from OpenInference
from openinference.instrumentation.litellm import LiteLLMInstrumentor

# Instrument LiteLLM
LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Setup

```python
import os
os.environ["OPENAI_API_KEY"] = "PASTE_YOUR_API_KEY_HERE"
```

### Run LiteLLM

```python
import litellm

# Ensure the required API key (e.g., OPENAI_API_KEY) is set in your environment
completion_response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"content": "What's the capital of China?", "role": "user"}]
)
print(completion_response)
```

