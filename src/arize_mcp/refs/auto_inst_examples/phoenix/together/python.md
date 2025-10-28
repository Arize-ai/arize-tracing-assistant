### Install

```bash
pip install openai openinference-instrumentation-openai arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

# Import open inference dependencies

``` python
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
import os
import openai
```
# Setup OTel via our convenience function and autoinstrument

```python

# configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=False # Auto-instrument your app based on installed dependencies
)

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


client = openai.OpenAI(
  api_key=os.environ.get("TOGETHER_API_KEY"),
  base_url="https://api.together.xyz/v1",
)

response = client.chat.completions.create(
  model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
  messages=[
    {"role": "system", "content": "You are a travel agent. Be descriptive and helpful."},
    {"role": "user", "content": "Tell me the top 3 things to do in San Francisco"},
  ]
)

print(response.choices[0].message.content)

```