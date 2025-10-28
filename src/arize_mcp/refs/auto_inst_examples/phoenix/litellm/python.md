### Install

```bash
pip install openinference-instrumentation-litellm litellm
```

### Setup

```python
from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=True # Auto-instrument your app based on installed OI dependencies
)
```

### Setup

```python
import os
os.environ["OPENAI_API_KEY"] = "PASTE_YOUR_API_KEY_HERE"
```

### Run LiteLLM

```python
import litellm
completion_response = litellm.completion(model="gpt-3.5-turbo",
                   messages=[{"content": "What's the capital of China?", "role": "user"}])
print(completion_response)
```