### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # Needed for the example code
# Add other LLM provider API keys if used by Guardrails
```

### Install

```bash
pip install guardrails-ai openinference-instrumentation-guardrails arize-otel
```


### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.guardrails import GuardrailsInstrumentor

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),   
    api_key=os.getenv("ARIZE_API_KEY"),     
    project_name="my-guardrails-app"  
)

GuardrailsInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run Guardrails Example

```python
# Ensure OPENAI_API_KEY is set in your environment for this example
import openai
from guardrails import Guard
from guardrails.hub import TwoWords # Example validator

# Initialize Guardrails
guard = Guard().use(
    TwoWords() # Using a simple validator from the hub
)

# Make a call through Guardrails
# This will also make an underlying call to the OpenAI LLM
response = guard(
    llm_api=openai.chat.completions.create,
    prompt="What is another name for America?",
    model="gpt-3.5-turbo",
    max_tokens=1024,
    # You can add instructions or other parameters as needed by your spec
)

# Print the validated (or processed) response
if response.validation_passed:
    print(f"Validated Output: {response.validated_output}")
else:
    print(f"Validation Failed. Raw LLM Output: {response.raw_llm_output}")
    print(f"Validation Details: {response.validation_details}")
```

