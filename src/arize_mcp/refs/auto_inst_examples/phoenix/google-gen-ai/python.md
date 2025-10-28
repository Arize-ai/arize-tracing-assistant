### Install <a href="#install" id="install"></a>

```bash
pip install openinference-instrumentation-google-genai google-genai
```

### Setup

```python
export GEMINI_API_KEY=[your_key_here]
```

```python
from phoenix.otel import register
​
# Configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=True # Auto-instrument your app based on installed OI dependencies
)
```

### Observe

```python
import os
from google import genai
​
def send_message_multi_turn() -> tuple[str, str]:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    chat = client.chats.create(model="gemini-2.0-flash-001")
    response1 = chat.send_message("What is the capital of France?")
    response2 = chat.send_message("Why is the sky blue?")
​
    return response1.text or "", response2.text or ""
```

