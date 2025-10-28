
### Install

```bash
pip install pyautogen

pip install openinference-instrumentation-openai openai

pip install openinference-instrumentation-autogen

pip install arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Setup Tracing

```python
# Import Arize OTel registration
from arize.otel import register

# Import OpenInference instrumentors
from openinference.instrumentation.autogen import AutogenInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

# Setup OTel and Arize exporter
# set_global_tracer_provider=True can be helpful for complex agent interactions
tracer_provider = register(
    space_id="YOUR_SPACE_ID",
    api_key="YOUR_API_KEY",
    project_name="my-autogen-app",
    set_global_tracer_provider=True 
)

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
AutogenInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run AutoGen Example

```python
import autogen

# Configuration for the LLM (e.g., OpenAI)
# Ensure OPENAI_API_KEY is set in your environment if model is not "stub"
config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST", # Example: Set this env var to your config list
    # Sample OAI_CONFIG_LIST content (save as a JSON file or set as ENV var):
    # [
    #   {
    #     "model": "gpt-3.5-turbo",
    #     "api_key": "YOUR_OPENAI_API_KEY" # Can also be picked from env
    #   }
    # ]
    filter_dict={
        "model": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"] # Specify models you want to use
    }
)

# Create agents
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": config_list,
        "temperature": 0
    }
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False, # Set to a dict with work_dir if you need code execution
)

# Start a chat
user_proxy.initiate_chat(
    assistant,
    message="What is the capital of France? Reply TERMINATE when done.",
)

print("AutoGen chat initiated. Check Arize for traces.")
```

