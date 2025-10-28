### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # Needed for the OpenAI example
```

### Install

```bash
pip install instructor openinference-instrumentation-instructor openinference-instrumentation-openai arize-otel opentelemetry-sdk opentelemetry-exporter-otlp
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.instructor import InstructorInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor # Or your LLM client's instrumentor

# Ensure your API keys are set as environment variables
# ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
# ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # For the example

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),
    api_key=os.getenv("ARIZE_API_KEY"),
    project_name="my-instructor-app" # Choose a project name
)

# Instrument Instructor
InstructorInstrumentor().instrument(tracer_provider=tracer_provider)
# Instrument the underlying LLM client
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider) # Example for OpenAI

print("Instructor and OpenAI client instrumented for Arize.")
```

### Run Instructor Example

```python
import instructor
from pydantic import BaseModel
from openai import OpenAI # Ensure OPENAI_API_KEY is set

# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int

# Patch the OpenAI client with Instructor
# The OpenAI client itself will be instrumented by OpenAIInstrumentor
# InstructorInstrumentor will trace the .create call patched by instructor.from_openai
client = instructor.from_openai(OpenAI())

# Extract structured data
user_info_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=UserInfo, # Instructor specific
    messages=[{"role": "user", "content": "John Doe is 30 years old."}]
)

print(f"Name: {user_info_response.name}")
print(f"Age: {user_info_response.age}")

# Example with validation error
try:
    invalid_user_info = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=UserInfo,
        messages=[{"role": "user", "content": "The user is Jane."}], # Age is missing
        max_retries=1 # Optional: limit retries for demonstration
    )
except Exception as e:
    print(f"Failed to extract valid UserInfo: {e}")
```

