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
from phoenix.otel import register

tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=True # Auto-instrument your app based on installed dependencies
)
```

### Run your Agent

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")
result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)
```