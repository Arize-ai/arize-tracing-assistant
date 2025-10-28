# Manual Instrumentation Example with Arize

Demonstrates how to manually add OpenTelemetry + OpenInference tracing to a Streamlit RAG application and export spans to **Arize**.

---

## 0. Prerequisites

```bash
pip install streamlit langchain langgraph openai openinference-semconv \
            opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc \
            arize-otel python-dotenv

# Arize credentials (replace with your values)
export ARIZE_SPACE_KEY="<your-space-key>"
export ARIZE_API_KEY="<your-api-key>"
```

---

## 1. Imports & environment bootstrap

```python
from dotenv import load_dotenv

# app dependencies
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from langchain import hub
from langchain_core.documents import Document

from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

# instrumanetation 
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk import trace as trace_sdk
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as OTLPSpanExporterGrpc,
)
from opentelemetry import trace as trace_api

load_dotenv()
```

---

## 2. TracerProvider registration (Arize)

The provider is cached with Streamlit so it is only created **once**, avoiding the "Overriding of current TracerProvider is not allowed" error on every rerun.

```python
# We wrap tracer-provider initialization in a Streamlit-cached function so it
# executes only once, preventing the "Overriding of current TracerProvider is
# not allowed" error when Streamlit re-runs the script.
@st.cache_resource(show_spinner=False)
def _init_tracer_provider() -> trace_sdk.TracerProvider:  # type: ignore
    """Initialize and register the global TracerProvider (runs once)."""

    tracer_provider = register(
        space_id="ARIZE_SPACE_ID",
        api_key="ARIZE_API_KEY",
        project_name="my-manually-instrumented-project",
    )
    return tracer_provider.get_tracer(__name__)

# Initialize once at import time
_TRACER_PROVIDER = _init_tracer_provider()
```

---

## 3. Model, embeddings & vector store setup

```python
llm = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings).load(
    "vector_store_openai.json", embeddings
)
```

---

## 4. Prompt template & application state

```python
prompt = hub.pull("rlm/rag-prompt")

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
```

---

## 5. Instrumented workflow steps

Each step starts its **own span** and records OpenInference semantic attributes so downstream observability tools (Arize, Phoenix, etc.) can reconstruct the RAG pipeline.

```python
def retrieve(state: State):
    tracer = trace_api.get_tracer(__name__)
    with tracer.start_as_current_span(
        "retrieve",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.RETRIEVER.value,
            SpanAttributes.INPUT_VALUE: state["question"],
        },
    ) as span:
        retrieved_docs = vector_store.similarity_search(state["question"])
        span.set_attribute(
            SpanAttributes.RETRIEVAL_DOCUMENTS,
            [doc.page_content[:200] for doc in retrieved_docs],
        )
    return {"context": retrieved_docs}


def generate(state: State):
    tracer = trace_api.get_tracer(__name__)
    with tracer.start_as_current_span(
        "generate",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.LLM.value,
            "llm.model": "claude-3-5-sonnet-latest",
            SpanAttributes.INPUT_VALUE: state["question"],
            "rag.context_length": len(state["context"]),
        },
    ) as span:
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(response.content))
    return {"answer": response.content}
```

---

## 6. LangGraph orchestration

```python
graph_builder = StateGraph(State)
graph_builder.add_node(retrieve)
graph_builder.add_node(generate)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")

graph = graph_builder.compile()
```

---

## 7. Streamlit UI & runtime

```python
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/One_Ring_Blender_Render.png/1280px-One_Ring_Blender_Render.png"
st.image(image_url, width=300)
st.title("Lord of the Rings RAG App")
st.write("Ask the model and you shall know.")

query = st.text_input("Enter your question:")

if query:
    # Start a trace (a root span) when the app is invoked, the Agent span is the parent span and wraps the following spans for each step    
    tracer = trace_api.get_tracer(__name__)
    with tracer.start_as_current_span(
        name="rag_query",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.AGENT.value,
            SpanAttributes.INPUT_VALUE: query,
        },
    ) as root_span:
        result = graph.invoke({"question": query})
        root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, result["answer"])
        st.write(result["answer"])
        with st.expander("Context"):
            st.write(result["context"])
```

---


