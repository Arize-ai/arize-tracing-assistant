### Install

```bash
pip install openinference-instrumentation-openai-agents openai-agents arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Setup

```python
from arize.otel import register

tracer_provider = register(
    space_id = "your-space-id", # in app space settings page
    api_key = "your-api-key", # in app space settings page
    project_name="agents"
)

from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run your Agent

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```