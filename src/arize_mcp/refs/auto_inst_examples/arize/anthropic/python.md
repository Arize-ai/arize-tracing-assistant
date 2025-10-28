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

# Import openinference instrumentor to map Anthropic traces to a standard format
from openinference.instrumentation.anthropic import AnthropicInstrumentor

# Turn on the instrumentor
AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run Anthropic

```python
import anthropic

client = anthropic.Anthropic() # The client will use the ANTHROPIC_API_KEY environment variable

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Why is the ocean salty?"
                }
            ]
        }
    ]
)
print(message.content)
```

