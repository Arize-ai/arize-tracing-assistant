### Install

```bash
pip install openinference-instrumentation-langchain langchain langchain-openai arize-otel opentelemetry-sdk opentelemetry-exporter-otlp
```

### API Key Setup

```bash
export ARIZE_SPACE_ID="YOUR_ARIZE_SPACE_ID"
export ARIZE_API_KEY="YOUR_ARIZE_API_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # For LangChain examples using OpenAI
# Add other LLM provider API keys if used by LangChain components
```

### Setup Tracing

```python
import os
from arize.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

# Ensure your API keys are set as environment variables
# ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
# ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # For the example

# Setup OTel via Arize's convenience function
tracer_provider = register(
    space_id=os.getenv("ARIZE_SPACE_ID"),    # or directly pass your Space ID
    api_key=os.getenv("ARIZE_API_KEY"),      # or directly pass your API Key
    project_name="my-langchain-app"        # Choose a project name
)

# Instrument LangChain
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

print("LangChain instrumented for Arize (Python).")
```

### Run LangChain Example (Python)

```python
# Ensure OPENAI_API_KEY is set in your environment
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("Why is the {celestial_object} {color}?").partial(celestial_object="sky")
# model_name can be gpt-3.5-turbo, gpt-4, etc.
# Ensure your OPENAI_API_KEY has access to the model you choose.
chain = prompt | ChatOpenAI(model_name="gpt-3.5-turbo") 

response = chain.invoke({"color": "blue"})
print(response.content)

# Example with a different model (if you have access and the key set up)
# from langchain_anthropic import ChatAnthropic
# chain_anthropic = prompt | ChatAnthropic(model_name="claude-3-opus-20240229")
# response_anthropic = chain_anthropic.invoke({"color": "red"})
# print(response_anthropic.content)
```

