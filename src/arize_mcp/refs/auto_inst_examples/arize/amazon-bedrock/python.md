### Install

```bash
pip install openinference-instrumentation-bedrock arize-otel
```

### API Key

```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key'
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

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.bedrock import BedrockInstrumentor

# Start the instrumentor for Bedrock
BedrockInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Setup

```python
import boto3
import os # For environment variables
import time # For session_id generation

# Ensure AWS credentials and region are set, e.g., via environment variables
# or other configuration methods compatible with boto3.
session = boto3.session.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"), # Optional
    region_name=os.environ.get("AWS_REGION_NAME")
)

# IMPORTANT: Use bedrock-agent-runtime for agents
client = session.client("bedrock-agent-runtime")

# Define your Agent ID and Alias ID (replace with your actual IDs)
AGENT_ID = "YOUR_AGENT_ID"
AGENT_ALIAS_ID = "YOUR_AGENT_ALIAS_ID"

# Example input text, replace as needed
input_text = "Tell me a joke about software development."
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

# Example of processing the response (optional, from Arize docs)
# You might want to print or otherwise use the response content
print(f"Invoked agent with session_id: {session_id}")
for i, event in enumerate(response["completion"]):
    if "chunk" in event:
        chunk_data = event["chunk"]
        if "bytes" in chunk_data:
            output_text_part = chunk_data["bytes"].decode("utf8")
            print(output_text_part, end="")
    elif "trace" in event:
        # Trace data can also be part of the event stream
        # print(f"Trace event: {event['trace']}") # Usually verbose
        pass
print() # for newline after streaming
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

# Import the automatic instrumentor from OpenInference
from openinference.instrumentation.bedrock import BedrockInstrumentor

# Start the instrumentor for Bedrock
BedrockInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Setup

```python
import boto3
import os # For environment variables
import json # For handling response

# Ensure AWS credentials and region are set, e.g., via environment variables
# or other configuration methods compatible with boto3.
# Example assuming environment variables:
session = boto3.session.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"), # Optional, depending on your auth
    region_name=os.environ.get("AWS_REGION_NAME")
)
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

