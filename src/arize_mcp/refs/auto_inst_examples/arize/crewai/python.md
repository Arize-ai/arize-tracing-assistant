### Install

```bash
# Install CrewAI and common tools
pip install crewai crewai-tools

# Install OpenInference instrumentor for CrewAI
pip install openinference-instrumentation-crewai

# Install OpenInference instrumentor for the underlying LLM handler
pip install openinference-instrumentation-langchain

# If CrewAI uses LiteLLM (check your CrewAI version/setup), you might need:
pip install openinference-instrumentation-litellm

# Install Arize OTel
pip install arize-otel
```

### API Key Setup

```bash
export OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
export SERPER_API_KEY='YOUR_SERPER_API_KEY'
```


### Setup Tracing

```python
# Import Arize OTel registration
from arize.otel import register

# Import OpenInference instrumentors, use either Langchain or LiteLLM
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor

# Setup OTel and Arize exporter
tracer_provider = register(
    space_id="YOUR_SPACE_ID",
    api_key="YOUR_API_KEY",
    project_name="my-crewai-app"
)

# Instrument CrewAI
CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Instrument the underlying LLM call handler (e.g., LangChain)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
# If using LiteLLM directly via a newer CrewAI version for model calls:
LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
```

### Run CrewAI Example

```python
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Ensure API keys are set in the environment as shown in "API Key Setup"
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
# os.environ["SERPER_API_KEY"] = "YOUR_SERPER_API_KEY"

search_tool = SerperDevTool()

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover cutting-edge developments in AI and data science',
  backstory="""You work at a leading tech think tank.
  Your expertise lies in identifying emerging trends.
  You have a knack for dissecting complex data and presenting actionable insights.""",
  verbose=True,
  allow_delegation=False,
  tools=[search_tool]
  # llm=ChatOpenAI(model_name="gpt-3.5-turbo") # Optionally specify an LLM instance here
)

writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling content on tech advancements',
  backstory="""You are a renowned Content Strategist, known for your insightful and engaging articles.
  You transform complex concepts into compelling narratives.""",
  verbose=True,
  allow_delegation=True
)

# Create tasks for your agents
task1 = Task(
  description="""Conduct a comprehensive analysis of the latest advancements in AI in 2024.
  Identify key trends, breakthrough technologies, and potential industry impacts.""",
  expected_output="Full analysis report in bullet points",
  agent=researcher
)

task2 = Task(
  description="""Using the insights provided, develop an engaging blog
  post that highlights the most significant AI advancements.
  Your post should be informative yet accessible, catering to a tech-savvy audience.
  Make it sound cool, avoid complex words so it doesn't sound like AI.""",
  expected_output="Full blog post of at least 4 paragraphs",
  agent=writer
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer],
  tasks=[task1, task2],
  verbose=False, # Set to True or 2 for more detailed logging
  process=Process.sequential # Default is sequential, can be hierarchical
)

# Get your crew to work!
print("Kicking off the crew...")
result = crew.kickoff()

print("######################")
print("CrewAI run completed. Result:")
print(result)
print("######################")
print("Check Arize for traces.")
```

