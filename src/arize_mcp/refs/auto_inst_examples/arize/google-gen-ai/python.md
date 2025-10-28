
### Install

```bash
pip install openinference-instrumentation-google-genai google-genai arize-otel
```

### API Key Setup

```bash
export GEMINI_API_KEY='your_gemini_api_key'
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
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

# Instrument the Google GenAI client
GoogleGenAIInstrumentor().instrument(tracer_provider=tracer_provider)
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

