### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # For LlamaIndex examples using OpenAI
```

### Install

```bash
pip install llama-index openinference-instrumentation-llama-index arize-otel opentelemetry-sdk opentelemetry-exporter-otlp
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

# Ensure your API keys are set as environment variables
# ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
# ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # For the example

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),
    api_key=os.getenv("ARIZE_API_KEY"),
    project_name="my-llamaindex-workflows-app" # Choose a project name
)

# Instrument LlamaIndex (this covers Workflows as well)
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

print("LlamaIndex (including Workflows) instrumented for Arize.")
```

### Run LlamaIndex Workflows Example

```python
# Example (conceptual - refer to LlamaIndex documentation for specific Workflow examples)
# Ensure OPENAI_API_KEY is set in your environment

from llama_index.core.workflow import (    
    Workflow,
    Event,
    Context,
    step
)
from llama_index.llms.openai import OpenAI # Example LLM

# Define a simple workflow (from LlamaIndex docs, adapted for context)
@step()
def add_one(val: int) -> Context:
    print(f"Adding one to {val}")
    return Context(value = val + 1)

@step()
def multiply_by_llm_output(context: Context, query: str) -> Context:
    print(f"Multiplying {context.get('value')} by LLM output for query: {query}")
    llm = OpenAI(model="gpt-3.5-turbo")
    response = llm.complete(f"Return a single number: {query}").text
    try:
        multiplier = int(response.strip())
        return Context(value = context.get('value') * multiplier, llm_response=response)
    except ValueError:
        print(f"Could not parse LLM output as integer: {response}")
        return Context(value = context.get('value'), llm_response=response, error="LLM output not an int")

my_workflow = Workflow(timeout=60) #name="My Simple Workflow", description="Adds one then multiplies by an LLM-generated number")
my_workflow.add_step(add_one, initial_value=Event())
my_workflow.add_step(multiply_by_llm_output, prev_step_output=True, query=Event())

# Run the workflow
initial_value = 5
query_for_llm = "What is 2 + 2?"
try:
    result_context = my_workflow.run(initial_value=initial_value, query=query_for_llm)
    print(f"Workflow Result: {result_context.get('value')}")
    if result_context.get('error'):
        print(f"Error during execution: {result_context.get('error')}")
except Exception as e:
    print(f"Workflow failed: {e}")
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),
    api_key=os.getenv("ARIZE_API_KEY"),
    project_name="my-llamaindex-app" # Choose a project name
)

# Instrument LlamaIndex
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run LlamaIndex Example

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("Some question about the data should go here")
print(response)
```

