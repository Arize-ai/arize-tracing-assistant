### Install

```bash
pip install openinference-instrumentation-mistralai mistralai
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

