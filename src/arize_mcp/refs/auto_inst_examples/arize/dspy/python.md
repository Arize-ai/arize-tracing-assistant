### Install

```bash
# Install DSPy framework
pip install dspy-ai

# Install OpenInference instrumentor for DSPy
pip install openinference-instrumentation-dspy

# Install LiteLLM and its OpenInference instrumentor (DSPy often uses LiteLLM)
pip install litellm openinference-instrumentation-litellm

# Install Arize OTel
pip install arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
# Other keys like ANTHROPIC_API_KEY, COHERE_API_KEY, etc., if using those models via LiteLLM.
```

### Setup Tracing

```python
# Import Arize OTel registration
from arize.otel import register

# Import OpenInference instrumentors
from openinference.instrumentation.dspy import DSPyInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor # For underlying LLM calls via LiteLLM

# Setup OTel and Arize exporter
tracer_provider = register(
    space_id="YOUR_SPACE_ID",
    api_key="YOUR_API_KEY",
    project_name="my-dspy-app"
)

# Instrument DSPy
DSPyInstrumentor().instrument(tracer_provider=tracer_provider)

# Instrument LiteLLM (recommended for full visibility into DSPy's LLM calls)
LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)

print("DSPy and LiteLLM instrumented for Arize.")
```

### Run DSPy Example

```python
import dspy
import os
from openinference.semconv.trace import SpanAttributes # For using_attributes
from openinference.instrumentation import using_attributes # For custom attributes

# Ensure OPENAI_API_KEY is set in your environment
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

if __name__ == "__main__":
    # Configure the LLM. DSPy can use various LLMs, often via LiteLLM.
    # For OpenAI models, ensure OPENAI_API_KEY is set.
    # The dspy.OpenAI client might internally use LiteLLM or a direct OpenAI client.
    turbo = dspy.OpenAI(model="gpt-3.5-turbo")
    dspy.settings.configure(lm=turbo)

    # Example of adding custom attributes to traces using OpenInference context manager
    with using_attributes(
        session_id="my-dspy-session-001",
        user_id="user-dspy-example",
        metadata={
            "environment": "testing",
            "dspy_module": "BasicQA",
        },
        tags=["dspy", "qa"],
        prompt_template_version="1.0",
        prompt_template_variables={
            "signature_desc": BasicQA.__doc__.strip()
        }
    ):
        # Define the predictor.
        generate_answer = dspy.Predict(BasicQA)

        # Call the predictor on a particular input.
        pred = generate_answer(
            question="What is the capital of the United States?"
        )
        print(f"Question: What is the capital of the United States?")
        print(f"Predicted Answer: {pred.answer}")

        pred_europe = generate_answer(
            question="What is the capital of France?"
        )
        print(f"Question: What is the capital of France?")
        print(f"Predicted Answer: {pred_europe.answer}")

    print("DSPy example run complete. Check Arize for traces.")
```

