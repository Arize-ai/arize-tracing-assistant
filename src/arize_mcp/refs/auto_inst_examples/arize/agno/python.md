### Install

```bash
pip install openinference-instrumentation-agno agno arize-otel
```

### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # Since the example uses OpenAIChat
```

### Setup

```python
from arize.otel import register
from openinference.instrumentation.agno import AgnoInstrumentor

# Configure the Arize tracer and exporter
tracer_provider = register(
    space_id="YOUR_ARIZE_SPACE_ID", # Replace with your Arize Space ID
    api_key="YOUR_ARIZE_API_KEY",   # Replace with your Arize API Key
    project_name="my-agno-app"      # Choose a project name
)

# Instrument Agno
AgnoInstrumentor().instrument(tracer_provider=tracer_provider)

print("Agno instrumented for Arize.")
```

### Run Agno

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    markdown=True,
    debug_mode=True,
)

agent.run("What is currently trending on Twitter?")
```

