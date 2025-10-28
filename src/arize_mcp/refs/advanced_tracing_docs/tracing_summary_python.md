# Arize Tracing Documentation - Python

This comprehensive guide covers OpenTelemetry tracing for Python applications with Arize, consolidating all essential information for LLM observability.

---

## Index
1. Installation & Setup
2. Auto-Instrumentation Catalogue
3. Auto-Instrumentation with context helpers
4. Manual Instrumentation
5. Span Kinds, Attributes & Semantic Conventions
6. Events, Exceptions & Status Handling
7. Context Propagation Recipes
8. Prompt Templates & Variables
9. Masking, Redaction & Span Filtering
10. Offline Evaluations & Experiments

---

## 1. Installation & Setup
[SECTION:SETUP]

### Basic Installation
```bash
pip install arize-otel opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc
```

### Quick Setup with arize.otel.register
```python
from arize.otel import register

tracer_provider = register(
    space_id="<ARIZE_SPACE_ID>",    # Found in space settings page
    api_key="<ARIZE_API_KEY>",      # Found in space settings page
    project_name="my-llm-app"       # Arbitrary label that groups traces
)
```

This function:
- Configures OTLP exporter streaming to `https://otlp.arize.com/v1`
- Sets global TracerProvider for downstream libraries
- Returns provider handle for advanced customization

### Advanced OTEL Configuration
For more control over span processing, resource attributes, and exporters:

```python
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

# Set authentication headers
headers = f"space_id={ARIZE_SPACE_ID},api_key={ARIZE_API_KEY}"
os.environ['OTEL_EXPORTER_OTLP_TRACES_HEADERS'] = headers

# Set resource attributes
trace_attributes = {
    "model_id": "your model name",      # Model identifier in Arize
    "model_version": "v1",              # Version for filtering
}

# Configure tracer provider
endpoint = "https://otlp.arize.com/v1"
tracer_provider = trace_sdk.TracerProvider(
    resource=Resource(attributes=trace_attributes)
)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint)))
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Get tracer instance
tracer = trace_api.get_tracer(__name__)
```

---

## 2. Auto-Instrumentation Catalogue
[SECTION:AUTO]

Install the instrumentor for your framework:

### Python Frameworks
```bash
# Example: OpenAI
pip install openinference-instrumentation-openai
```

Available frameworks include: OpenAI, Anthropic, LangChain, LlamaIndex, DSPy, Haystack, Amazon Bedrock, Mistral, Google Generative AI, Vertex AI, Groq, LiteLLM, Instructor, CrewAI, AutoGen, Guardrails AI, Ragas, CleanLab, and more. Simply replace `openai` in the package name with your framework of choice.

### Basic Auto-Instrumentation
```python
from openinference.instrumentation.openai import OpenAIInstrumentor

# Apply instrumentation
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

# Your OpenAI calls now automatically create spans
```

---

## 3. Auto-Instrumentation with Context Helpers and Decorators
[SECTION:DECORATORS]

### 3.1 Enriching Auto-Instrumented Spans
```python
from opentelemetry import trace

# Get current span created by auto-instrumentation
current_span = trace.get_current_span()

# Add custom attributes
current_span.set_attribute("operation.value", 1)
current_span.set_attribute("operation.name", "Saying hello!")
current_span.set_attribute("operation.other-stuff", [1, 2, 3])
```

### 3.2 OpenInference Semantic Attributes
```python
from openinference.semconv.trace import SpanAttributes, MessageAttributes

span.set_attribute(SpanAttributes.OUTPUT_VALUE, response)

# Populate output messages table
span.set_attribute(
    f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.{MessageAttributes.MESSAGE_ROLE}",
    "assistant",
)
span.set_attribute(
    f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.{MessageAttributes.MESSAGE_CONTENT}",
    response,
)
```

### 3.3 Context Propagation Helpers
```python
from openinference.instrumentation import (
    using_metadata, using_tags, using_prompt_template, 
    using_attributes, get_attributes_from_context
)

# Metadata propagation
with using_metadata({"run_id": "abc-123", "env": "prod"}):
    # All child spans inherit this metadata
    client.chat.completions.create(...)

# Tags propagation  
with using_tags(["rag", "retrieval"]):
    # All child spans inherit these tags
    pass

# Prompt template propagation
with using_prompt_template(
    template="Describe the weather in {city}",
    variables={"city": "Johannesburg"},
    version="v1.0",
):
    # Template info attached to spans
    pass

# Combined attributes
with using_attributes(
    session_id="sess-42",
    user_id="user-007",
    metadata={"run": 7},
    tags=["agent"],
):
    # All attributes propagate to child spans
    pass

# Retrieve context attributes in manual spans
with tracer.start_as_current_span("custom") as span:
    span.set_attributes(dict(get_attributes_from_context()))
```

### 3.4 OpenInference Decorators

```python
from openinference.instrumentation import TracerProvider
from arize.otel import register

# Get tracer with decorators
tracer_provider = register(...)
tracer = tracer_provider.get_tracer(__name__)

# Chain decorator
@tracer.chain
def process_request(input: str) -> str:
    # Input/output automatically captured
    return "processed"

# Agent decorator
@tracer.agent
def agent_task(query: str) -> str:
    return "agent response"

# Tool decorator
@tracer.tool
def search_tool(query: str, limit: int) -> list:
    """Search tool description"""
    return ["result1", "result2"]

# LLM decorator
@tracer.llm
def llm_request(prompt: str) -> str:
    return "llm response"

```

### 3.5 Suppress Tracing
```python
from openinference.instrumentation import suppress_tracing

with suppress_tracing():
    # No spans created here
    client.chat.completions.create(...)
```

---

## 4. Manual Instrumentation
[SECTION:MANUAL]

### 4.1 Basic Manual Spans
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("input.value", "user query")
    # Your logic here
    result = process_data()
    span.set_attribute("output.value", result)
```

### 4.2 Span Types with Attributes

#### LLM Spans
```python
from openinference.semconv.trace import SpanAttributes

with tracer.start_as_current_span("llm-call") as span:
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, "LLM")
    span.set_attribute(SpanAttributes.LLM_MODEL_NAME, "gpt-4")
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_PROMPT, prompt_tokens)
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_COMPLETION, completion_tokens)
    span.set_attribute(SpanAttributes.LLM_TOKEN_COUNT_TOTAL, total_tokens)
    
    # Input messages
    for idx, msg in enumerate(messages):
        span.set_attribute(
            f"{SpanAttributes.LLM_INPUT_MESSAGES}.{idx}.{MessageAttributes.MESSAGE_ROLE}",
            msg["role"]
        )
        span.set_attribute(
            f"{SpanAttributes.LLM_INPUT_MESSAGES}.{idx}.{MessageAttributes.MESSAGE_CONTENT}",
            msg["content"]
        )
    
    # Make LLM call
    response = llm_client.complete(messages)
    
    # Output messages
    span.set_attribute(
        f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.{MessageAttributes.MESSAGE_ROLE}",
        "assistant"
    )
    span.set_attribute(
        f"{SpanAttributes.LLM_OUTPUT_MESSAGES}.0.{MessageAttributes.MESSAGE_CONTENT}",
        response.content
    )
```

#### Retriever Spans
```python
from openinference.semconv.trace import OpenInferenceSpanKindValues

with tracer.start_as_current_span("vector-search") as span:
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.RETRIEVER.value)
    span.set_attribute(SpanAttributes.INPUT_VALUE, query_text)
    
    try:
        documents = search_client.search(query_text)
        for i, doc in enumerate(documents):
            span.set_attribute(f"retrieval.documents.{i}.document.id", doc["id"])
            span.set_attribute(f"retrieval.documents.{i}.document.score", doc["score"])
            span.set_attribute(f"retrieval.documents.{i}.document.content", doc["content"])
            span.set_attribute(f"retrieval.documents.{i}.document.metadata", str(doc["metadata"]))
        
        span.set_status(Status(StatusCode.OK))
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR))
        span.record_exception(e)
```

#### Tool Spans
```python
from openinference.semconv.trace import ToolCallAttributes

with tracer.start_as_current_span("tool-execution") as span:
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.TOOL.value)
    span.set_attribute(ToolCallAttributes.TOOL_CALL_FUNCTION_NAME, tool_name)
    span.set_attribute(ToolCallAttributes.TOOL_CALL_FUNCTION_ARGUMENTS_JSON, json.dumps(tool_args))
    
    # Execute tool
    result = tool_function(**tool_args)
    
    span.set_attribute("message.tool_calls.0.tool_call.function.output", result)
```

#### Embedding Spans
```python
from openinference.semconv.trace import EmbeddingAttributes

with tracer.start_as_current_span("generate-embeddings") as span:
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.EMBEDDING.value)
    span.set_attribute(SpanAttributes.EMBEDDING_MODEL_NAME, "text-embedding-ada-002")
    
    embeddings = embedding_model.embed(texts)
    
    for i, (text, vector) in enumerate(zip(texts, embeddings)):
        span.set_attribute(f"{SpanAttributes.EMBEDDING_EMBEDDINGS}.{i}.{EmbeddingAttributes.EMBEDDING_TEXT}", text)
        span.set_attribute(f"{SpanAttributes.EMBEDDING_EMBEDDINGS}.{i}.{EmbeddingAttributes.EMBEDDING_VECTOR}", vector)
```

#### Reranker Spans
```python
with tracer.start_as_current_span("rerank-documents") as span:
    span.set_attribute(SpanAttributes.OPENINFERENCE_SPAN_KIND, OpenInferenceSpanKindValues.RERANKER.value)
    span.set_attribute(SpanAttributes.RERANKER_QUERY, query)
    span.set_attribute(SpanAttributes.RERANKER_MODEL_NAME, "cross-encoder/ms-marco-MiniLM-L-12-v2")
    span.set_attribute(SpanAttributes.RERANKER_TOP_K, top_k)
    span.set_attribute(SpanAttributes.RERANKER_INPUT_DOCUMENTS, str(input_docs))
    
    reranked_docs = reranker.rerank(query, input_docs, top_k)
    
    span.set_attribute(SpanAttributes.RERANKER_OUTPUT_DOCUMENTS, str(reranked_docs))
```

### 4.3 General Span Attributes
```python
# Common attributes for any span type
span.set_attribute(SpanAttributes.INPUT_VALUE, "<INPUT>")
span.set_attribute(SpanAttributes.INPUT_MIME_TYPE, "text/plain")
span.set_attribute(SpanAttributes.OUTPUT_VALUE, "<OUTPUT>")
span.set_attribute(SpanAttributes.OUTPUT_MIME_TYPE, "text/plain")
span.set_attribute(SpanAttributes.TAG_TAGS, str(["tag1", "tag2"]))
span.set_attribute(SpanAttributes.METADATA, json.dumps({"key": "value"}))
```

---

## 5. Span Kinds, Attributes & Semantic Conventions
[SECTION:SEMANTIC]

### OpenInference Span Kinds
| Span Kind | Description | Use Case |
|-----------|-------------|----------|
| CHAIN | General logic operations | Functions, code blocks |
| LLM | LLM invocations | Chat completions, text generation |
| TOOL | Tool/function calls | External APIs, calculations |
| RETRIEVER | Document retrieval | Vector search, database queries |
| EMBEDDING | Embedding generation | Text/image embeddings |
| AGENT | Agent invocations | Top-level agent orchestration |
| RERANKER | Reranking operations | Result reordering |
| GUARDRAIL | Safety checks | Content filtering, validation |
| EVALUATOR | Evaluation runs | Model assessment |

### Key Semantic Conventions
```python
# Import semantic conventions
from openinference.semconv.trace import (
    SpanAttributes,
    MessageAttributes,
    ToolCallAttributes,
    EmbeddingAttributes,
    DocumentAttributes,
    ImageAttributes
)

# Common patterns
SpanAttributes.OPENINFERENCE_SPAN_KIND  # Span type
SpanAttributes.INPUT_VALUE              # Input data
SpanAttributes.OUTPUT_VALUE             # Output data
SpanAttributes.LLM_MODEL_NAME          # Model identifier
SpanAttributes.LLM_TOKEN_COUNT_*       # Token counts
SpanAttributes.LLM_INPUT_MESSAGES      # Chat messages
SpanAttributes.RETRIEVAL_DOCUMENTS     # Retrieved docs
SpanAttributes.EMBEDDING_EMBEDDINGS    # Embedding vectors
```

---

## 6. Events, Exceptions & Status Handling
[SECTION:EVENTS]

### 6.1 Adding Events
```python
current_span = trace.get_current_span()

# Log events during execution
current_span.add_event("Starting LLM call")
response = llm.complete(prompt)
current_span.add_event("LLM call completed", {
    "response.length": len(response),
    "model.temperature": 0.7
})
```

### 6.2 Setting Span Status
```python
from opentelemetry.trace import Status, StatusCode

try:
    result = risky_operation()
    current_span.set_status(Status(StatusCode.OK))
except Exception as e:
    current_span.set_status(Status(StatusCode.ERROR))
```

### 6.3 Recording Exceptions
```python
try:
    result = process_data()
except ValueError as e:
    current_span.set_status(Status(StatusCode.ERROR))
    current_span.record_exception(e)
    # Exception details are preserved in span
    raise
```

### 6.4 Complete Error Handling Pattern
```python
with tracer.start_as_current_span("data-processing") as span:
    span.add_event("Processing started")
    
    try:
        # Risky operation
        data = fetch_external_data()
        span.add_event("Data fetched successfully")
        
        result = transform_data(data)
        span.set_attribute("output.value", result)
        span.set_status(Status(StatusCode.OK))
        
    except ConnectionError as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, "Failed to fetch data"))
        span.add_event("Connection failed", {"retry.attempts": 3})
        raise
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR))
        raise
```

---

## 7. Context Propagation Recipes
[SECTION:CONTEXT]

### 7.1 Async Context Propagation
```python
import asyncio
from opentelemetry.context import attach, detach, get_current

tracer = trace.get_tracer(__name__)

async def async_operation(ctx):
    token = attach(ctx)
    try:
        current_span = trace.get_current_span()
        current_span.set_attribute("async.operation", "processing")
        await asyncio.sleep(1)
        current_span.add_event("Async operation completed")
    finally:
        detach(token)

def main_operation():
    with tracer.start_as_current_span("main") as span:
        context = get_current()
        # Pass context to async function
        asyncio.run(async_operation(context))
```

### 7.2 Thread Pool Context Propagation
```python
import concurrent.futures
from opentelemetry.context import attach, detach, get_current

def process_item(item, context):
    """Process item with proper context"""
    token = attach(context)
    try:
        span = trace.get_current_span()
        span.set_attribute("item.id", item["id"])
        # Process the item
        result = expensive_computation(item)
        span.add_event(f"Processed item {item['id']}")
        return result
    finally:
        detach(token)

def parallel_processing(items):
    with tracer.start_as_current_span("parallel-batch") as span:
        context = get_current()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Pass context to each thread
            futures = [
                executor.submit(process_item, item, context) 
                for item in items
            ]
            results = [f.result() for f in futures]
        
        span.set_attribute("batch.size", len(items))
        return results
```

### 7.3 Cross-Service Propagation
```python
import requests
from opentelemetry.propagators.textmap import DefaultTextMapPropagator

# Service A - Inject context into headers
def call_service_b():
    with tracer.start_as_current_span("call-service-b") as span:
        headers = {}
        # Inject trace context into headers
        DefaultTextMapPropagator().inject(carrier=headers)
        
        response = requests.get("http://service-b/api/endpoint", headers=headers)
        span.set_attribute("http.status_code", response.status_code)
        return response.json()

# Service B - Extract context from headers
from flask import Flask, request

app = Flask(__name__)

@app.route("/api/endpoint")
def endpoint():
    # Extract context from incoming request
    context = DefaultTextMapPropagator().extract(carrier=dict(request.headers))
    
    with tracer.start_as_current_span("process-request", context=context) as span:
        span.add_event("Received request from Service A")
        # Process request with proper trace context
        result = process_business_logic()
        return result
```

### 7.4 Custom Context Wrapper
```python
from typing import Callable, Any
from opentelemetry.context import attach, detach, get_current

def with_current_context(func: Callable) -> Callable:
    """Decorator that preserves trace context"""
    def wrapper(*args, **kwargs):
        context = get_current()
        token = attach(context)
        try:
            return func(*args, **kwargs)
        finally:
            detach(token)
    return wrapper

# Usage
@with_current_context
def background_task(data):
    span = trace.get_current_span()
    span.set_attribute("task.data", str(data))
    # Task executes with proper context
```

---

## 8. Prompt Templates & Variables
[SECTION:PROMPT]

### 8.1 Basic Prompt Template Instrumentation
```python
from openinference.instrumentation import using_prompt_template

prompt_template = "Please describe the weather forecast for {city} on {date}"
prompt_variables = {"city": "Johannesburg", "date": "July 11"}

with using_prompt_template(
    template=prompt_template,
    variables=prompt_variables,
    version="v1.0",
):
    # Format the prompt
    formatted_prompt = prompt_template.format(**prompt_variables)
    
    # Make LLM call - template info automatically attached to spans
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": formatted_prompt}]
    )
```

### 8.2 Template Versioning Pattern
```python
class PromptManager:
    def __init__(self):
        self.templates = {
            "v1.0": "Summarize this text: {text}",
            "v1.1": "Provide a concise summary of the following: {text}",
            "v2.0": "Create a {style} summary of: {text}"
        }
    
    def get_prompt(self, version, **variables):
        template = self.templates.get(version)
        
        with using_prompt_template(
            template=template,
            variables=variables,
            version=version
        ):
            return template.format(**variables)

# Usage
prompt_mgr = PromptManager()
prompt = prompt_mgr.get_prompt("v2.0", text=document, style="technical")
```

### 8.3 Dynamic Template Selection
```python
def generate_response(query_type, **kwargs):
    templates = {
        "question": "Answer this question: {question}",
        "translation": "Translate to {target_lang}: {text}",
        "summary": "Summarize in {max_words} words: {content}"
    }
    
    template = templates[query_type]
    
    with using_prompt_template(
        template=template,
        variables=kwargs,
        version="dynamic"
    ):
        prompt = template.format(**kwargs)
        return llm.complete(prompt)
```

---

## 9. Masking, Redaction & Span Filtering
[SECTION:MASK]

### 9.1 Environment Variable Masking
```python
import os

# Mask sensitive data via environment variables
os.environ["OPENINFERENCE_HIDE_INPUTS"] = "false"
os.environ["OPENINFERENCE_HIDE_OUTPUTS"] = "false"
os.environ["OPENINFERENCE_HIDE_INPUT_MESSAGES"] = "false"
os.environ["OPENINFERENCE_HIDE_OUTPUT_MESSAGES"] = "false"
os.environ["OPENINFERENCE_HIDE_INPUT_IMAGES"] = "true"
os.environ["OPENINFERENCE_HIDE_INPUT_TEXT"] = "false"
os.environ["OPENINFERENCE_HIDE_OUTPUT_TEXT"] = "false"
os.environ["OPENINFERENCE_HIDE_EMBEDDING_VECTORS"] = "true"
os.environ["OPENINFERENCE_BASE64_IMAGE_MAX_LENGTH"] = "1000"
```

### 9.2 TraceConfig Masking
```python
from openinference.instrumentation import TraceConfig
from openinference.instrumentation.openai import OpenAIInstrumentor

config = TraceConfig(
    hide_inputs=False,
    hide_outputs=False,
    hide_input_messages=False,
    hide_output_messages=False,
    hide_input_images=True,           # Hide image data
    hide_input_text=False,
    hide_output_text=False,
    hide_embedding_vectors=True,      # Hide large vectors
    base64_image_max_length=1000,     # Truncate images
)

OpenAIInstrumentor().instrument(
    tracer_provider=tracer_provider,
    config=config
)
```

### 9.3 Custom PII Redaction Processor
```python
import re
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter

class PIIRedactingSpanProcessor(SpanProcessor):
    def __init__(self, exporter: SpanExporter):
        self._exporter = exporter
        self._patterns = {
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        }
    
    def _redact_string(self, value: str) -> str:
        for name, pattern in self._patterns.items():
            value = pattern.sub(f'[REDACTED_{name.upper()}]', value)
        return value
    
    def _redact_value(self, value):
        if isinstance(value, str):
            return self._redact_string(value)
        elif isinstance(value, dict):
            return {k: self._redact_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._redact_value(item) for item in value]
        return value
    
    def on_end(self, span: ReadableSpan):
        # Create new attributes with redacted values
        redacted_attrs = {}
        for key, value in span.attributes.items():
            redacted_attrs[key] = self._redact_value(value)
        
        # Export span with redacted attributes
        # (Implementation depends on your exporter)
        self._exporter.export([span])
    
    def on_start(self, span, parent_context=None):
        pass
    
    def shutdown(self):
        self._exporter.shutdown()
    
    def force_flush(self, timeout_millis=30000):
        self._exporter.force_flush(timeout_millis)

# Use the PII processor
pii_processor = PIIRedactingSpanProcessor(OTLPSpanExporter(endpoint))
tracer_provider.add_span_processor(pii_processor)
```

### 9.4 Custom Sampling
```python
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision
from opentelemetry.context import Context

class ConditionalSampler(Sampler):
    """Sample based on span attributes"""
    
    def should_sample(self, parent_context: Context, trace_id: int, 
                     name: str, kind, attributes: dict, links):
        # Don't sample internal/debug spans
        if attributes.get("debug.internal"):
            return SamplingResult(Decision.DROP, {})
        
        # Always sample errors
        if attributes.get("error"):
            return SamplingResult(Decision.RECORD_AND_SAMPLE, {})
        
        # Sample 10% of normal traffic
        if trace_id % 10 == 0:
            return SamplingResult(Decision.RECORD_AND_SAMPLE, {})
        
        return SamplingResult(Decision.DROP, {})

# Apply custom sampler
tracer_provider = TracerProvider(sampler=ConditionalSampler())
```

---

## 10. Offline Evaluations & Experiments
[SECTION:EVAL]

### 10.1 Export Traces for Evaluation
```python
import os
from datetime import datetime
from arize.exporter import ArizeExportClient
from arize.utils.types import Environments

# Different API key for export
os.environ['ARIZE_API_KEY'] = ARIZE_API_KEY

client = ArizeExportClient()
traces_df = client.export_model_to_df(
    space_id='<SPACE_ID>',
    model_id='<MODEL_ID>',
    environment=Environments.TRACING,
    start_time=datetime.fromisoformat('2024-01-01T00:00:00'),
    end_time=datetime.fromisoformat('2024-01-02T00:00:00'),
)

# Prepare data for evaluation
traces_df["input"] = traces_df["attributes.input.value"]
traces_df["output"] = traces_df["attributes.output.value"]
```

### 10.2 Run Custom Evaluations
```python
from phoenix.evals import OpenAIModel, llm_classify

# Configure evaluator
eval_model = OpenAIModel(
    model="gpt-4o",
    temperature=0,
    api_key=os.environ["OPENAI_API_KEY"]
)

# Define evaluation template
EVAL_TEMPLATE = '''
You are evaluating response quality.
[Question]: {input}
[Response]: {output}

Rate the response as either "good", "acceptable", or "poor".
Consider accuracy, completeness, and clarity.
'''

# Run evaluation
evals_df = llm_classify(
    dataframe=traces_df,
    template=EVAL_TEMPLATE,
    model=eval_model,
    rails=["good", "acceptable", "poor"]
)
```

### 10.3 Log Evaluations Back to Arize
```python
from arize.pandas.logger import Client
import pandas as pd

# Initialize Arize client
arize_client = Client(
    space_id=SPACE_ID,
    api_key=API_KEY,
    developer_key=DEVELOPER_KEY
)

# Prepare evaluation dataframe
evals_df = evals_df.set_index(traces_df["context.span_id"])

# Send evaluations
arize_client.log_evaluations_sync(
    dataframe=evals_df,
    project_name='YOUR_PROJECT_NAME'
)
```

### 10.4 Custom Evaluation Functions
```python
def evaluate_response_length(row):
    """Custom evaluation for response length"""
    response = row['output']
    if len(response) < 50:
        return {
            'eval.length.label': 'too_short',
            'eval.length.score': 0.0,
            'eval.length.explanation': 'Response under 50 characters'
        }
    elif len(response) > 500:
        return {
            'eval.length.label': 'too_long', 
            'eval.length.score': 0.0,
            'eval.length.explanation': 'Response over 500 characters'
        }
    else:
        return {
            'eval.length.label': 'appropriate',
            'eval.length.score': 1.0,
            'eval.length.explanation': 'Response length within range'
        }

# Apply custom evaluation
custom_evals = traces_df.apply(evaluate_response_length, axis=1)
eval_df = pd.DataFrame(custom_evals.tolist())
eval_df['context.span_id'] = traces_df['context.span_id']

# Log custom evaluations
arize_client.log_evaluations_sync(eval_df, 'YOUR_PROJECT_NAME')
```

---
