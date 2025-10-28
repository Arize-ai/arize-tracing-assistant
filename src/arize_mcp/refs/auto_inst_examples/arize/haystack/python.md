### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # Needed for the OpenAIGenerator example
# Add other LLM provider API keys if used by Haystack components
```

### Install

```bash
pip install haystack-ai openinference-instrumentation-haystack arize-otel
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.haystack import HaystackInstrumentor

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),    # or directly pass your Space ID
    api_key=os.getenv("ARIZE_API_KEY"),      # or directly pass your API Key
    project_name="my-haystack-app"         # Choose a project name
)

# Instrument Haystack
HaystackInstrumentor().instrument(tracer_provider=tracer_provider)

print("Haystack instrumented for Arize.")
```

### Run Haystack Example

```python
# Ensure OPENAI_API_KEY is set in your environment for this example
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder # Added for a more complete example

# Define a prompt template
prompt_template = """
Answer the following question based on your knowledge.
Question: {{question}}
Answer:
"""

# Initialize the pipeline
pipeline = Pipeline()

# Initialize Haystack components
prompt_builder = PromptBuilder(template=prompt_template)
llm = OpenAIGenerator(model="gpt-3.5-turbo") # Uses OPENAI_API_KEY

# Add components to the pipeline
pipeline.add_component(name="prompt_builder", instance=prompt_builder)
pipeline.add_component(name="llm", instance=llm)

# Connect the components
pipeline.connect("prompt_builder.prompt", "llm.prompt")

# Define the question
question_to_ask = "What is the location of the Hanging Gardens of Babylon?"

# Run the pipeline
response = pipeline.run({
    "prompt_builder": {"question": question_to_ask}
})

# Print the response from the LLM
if response and "llm" in response and "replies" in response["llm"]:
    print(f"Question: {question_to_ask}")
    print(f"Answer: {response['llm']['replies'][0]}")
else:
    print(f"Failed to get a response or response format is unexpected: {response}")
```

