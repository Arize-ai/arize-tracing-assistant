### Install

```bash
pip install openinference-instrumentation-haystack haystack-ai
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

### Run Haystack

```python
from haystack import Pipeline
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders.prompt_builder import PromptBuilder

prompt_template = """
Answer the following question.
Question: {{question}}
Answer:
"""

# Initialize the pipeline
pipeline = Pipeline()

# Initialize the OpenAI generator component
llm = OpenAIGenerator(model="gpt-3.5-turbo")
prompt_builder = PromptBuilder(template=prompt_template)

# Add the generator component to the pipeline
pipeline.add_component("prompt_builder", prompt_builder)
pipeline.add_component("llm", llm)
pipeline.connect("prompt_builder", "llm")

# Define the question
question = "What is the location of the Hanging Gardens of Babylon?"
```

### Info
Phoenix's auto-instrumentor collects any traces from Haystack Pipelines. If you are using Haystack but not using Pipelines, you won't see traces appearing in Phoenix automatically.
If you don't want to use Haystack pipelines but still want tracing in Phoenix, you can use Using Phoenix Decorators instead of this auto-instrumentor.