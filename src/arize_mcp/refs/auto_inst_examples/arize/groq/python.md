### Install

```bash
pip install openinference-instrumentation-groq groq arize-otel
```

### API Key Setup

```bash
export GROQ_API_KEY='your_groq_api_key'
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
from openinference.instrumentation.groq import GroqInstrumentor

# Instrument the Groq client
GroqInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run Groq

```python
import os
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"), 
    # This is the default and can be omitted if GROQ_API_KEY is set
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of low latency LLMs",
        }
    ],
    model="mixtral-8x7b-32768",
)
print(chat_completion.choices[0].message.content)
```

