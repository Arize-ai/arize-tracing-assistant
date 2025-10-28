### Install

```bash
pip install openinference-instrumentation-mistralai mistralai arize-otel
```

### API Key Setup

```bash
export MISTRAL_API_KEY='your_mistral_api_key'
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

# Import openinference instrumentor to map Mistral traces to a standard format
from openinference.instrumentation.mistralai import MistralAIInstrumentor

# Turn on the instrumentor
MistralAIInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run Mistral

```python
import os

from mistralai import Mistral
from mistralai.models import UserMessage

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-tiny"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model=model,
    messages=[UserMessage(content="What is the best French cheese?")],
)
print(chat_response.choices[0].message.content)
```

