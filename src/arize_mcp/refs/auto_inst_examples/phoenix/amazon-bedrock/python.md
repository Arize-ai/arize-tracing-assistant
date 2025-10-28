### Install

```bash
pip install openinference-instrumentation-bedrock opentelemetry-exporter-otlp
```

### Setup

```python
from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=True # Auto-instrument your app based on installed OI dependencies
)
```

```python
import boto3

session = boto3.session.Session()
client = session.client("bedrock-runtime")
```

### Run Bedrock Agents

```python
session_id = f"default-session1_{int(time.time())}"

attributes = dict(
    inputText=input_text,
    agentId=AGENT_ID,
    agentAliasId=AGENT_ALIAS_ID,
    sessionId=session_id,
    enableTrace=True,
)
response = client.invoke_agent(**attributes)
```

### Setup

```python
from phoenix.otel import register

# configure the Phoenix tracer
tracer_provider = register(
  project_name="my-llm-app", # Default is 'default'
  auto_instrument=True # Auto-instrument your app based on installed OI dependencies
)
```

### Setup

```python
import boto3

session = boto3.session.Session()
client = session.client("bedrock-runtime")
```

### Run Bedrock

```python
prompt = (
    b'{"prompt": "Human: Hello there, how are you? Assistant:", "max_tokens_to_sample": 1024}'
)
response = client.invoke_model(modelId="anthropic.claude-v2", body=prompt)
response_body = json.loads(response.get("body").read())
print(response_body["completion"])
```

