### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export HF_TOKEN="YOUR_HUGGING_FACE_TOKEN" # Required by smolagents
```

### Install

```bash
pip install smolagents openinference-instrumentation-smolagents arize-otel opentelemetry-sdk opentelemetry-exporter-otlp
```

### Setup Tracing

```python
os.environ["HF_TOKEN"] = "<your_hf_token_value>"
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),
    api_key=os.getenv("ARIZE_API_KEY"),
    project_name="my-smolagents-app" # Choose a project name
)

SmolagentsInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Create & Run an Agent Example

```python
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    ManagedAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    HfApiModel,
)

model = HfApiModel()

agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
)
managed_agent = ManagedAgent(
    agent=agent,
    name="managed_agent",
    description="This is an agent that can do web search.",
)
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[managed_agent],
)
manager_agent.run(
    "If the US keeps its 2024 growth rate, how many years will it take for the GDP to double?"
)
```

