### Install

```bash
pip install openinference-instrumentation-vertexai arize-otel opentelemetry-sdk opentelemetry-exporter-otlp "opentelemetry-proto>=1.12.0"
```

### Setup OpenInference and autoinstrument
``` python
from openinference.instrumentation.vertexai import VertexAIInstrumentor
from arize.otel import register

tracer_provider = register(
    space_id = "your-space-id", # in app space settings page
    api_key = "your-api-key", # in app space settings page
    project_name = "your-project-name", # name this to whatever you would like
)

VertexAIInstrumentor().instrument(tracer_provider=tracer_provider)


import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

print(model.generate_content("Why is sky blue?"))

```

