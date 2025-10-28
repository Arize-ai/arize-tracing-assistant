# Manual Instrumentation Example with Phoenix

Demonstrates how to manually add OpenTelemetry + OpenInference tracing to a Streamlit RAG application and export spans to a **Phoenix** backend running locally.

---

## 0. Prerequisites

```bash
pip install streamlit langchain langgraph openai openinference-semconv \
            opentelemetry-sdk opentelemetry-exporter-otlp-proto-http \
            phoenix-tracing python-dotenv

# Spin up Phoenix locally (default port 6006)
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

---

## 1. Imports & environment bootstrap

```python
from dotenv import load_dotenv

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk import trace as trace_sdk
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace as trace_api

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from langchain import hub
from langchain_core.documents import Document

from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

load_dotenv()
```

---

## 2. TracerProvider registration (Phoenix)

The provider is cached so Streamlit only initializes it once.

```python
# Manually instrumentated streamlit RAG app for Phoenix using Open Telemetry and Open Inference
# -----------------------------------------------------------------------------------------


from dotenv import load_dotenv

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk import trace as trace_sdk
from openinference.semconv.trace import SpanAttributes, OpenInferenceSpanKindValues
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace as trace_api

import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from langchain import hub
from langchain_core.documents import Document

from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict


load_dotenv()


# We wrap tracer-provider initialization in a Streamlit-cached function so it
# executes only once, preventing the "Overriding of current TracerProvider is
# not allowed" error when Streamlit re-runs the script.
@st.cache_resource(show_spinner=False)
def _init_tracer_provider() -> trace_sdk.TracerProvider:  # type: ignore
    """Initialize and register the global TracerProvider (runs once)."""

    # If the current provider is already a real provider (i.e. not the default
    # no-op), reuse it to avoid overriding.
    current_provider = trace_api.get_tracer_provider()
    if isinstance(current_provider, trace_sdk.TracerProvider):
        return current_provider  # Already initialized

    trace_attributes = {
        "openinference.project_name": "my-manually-instrumented-project",
    }

    provider = trace_sdk.TracerProvider(resource=Resource(attributes=trace_attributes))

    exporter = OTLPSpanExporter(endpoint="http://localhost:6006/v1/traces")
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    trace_api.set_tracer_provider(provider)
    return provider


# Initialize the tracer provider once at import time
_TRACER_PROVIDER = _init_tracer_provider()


llm = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")

image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/One_Ring_Blender_Render.png/1280px-One_Ring_Blender_Render.png"
st.image(image_url, width=300)
st.title("Lord of the Rings RAG App")
st.write("Ask the model and you shall know.")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings).load(
    "vector_store_openai.json", embeddings
)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    tracer = trace_api.get_tracer(__name__)
    # Start a span for the retrieve step, enriching the span with Open Inference attributes
    with tracer.start_as_current_span(
        "retrieve",
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: OpenInferenceSpanKindValues.RETRIEVER.value,
            SpanAttributes.INPUT_VALUE: state["question"],
        },
    ) as span:
        retrieved_docs = vector_store.similarity_search(state["question"])

        # Attach retrieved docs (truncate to avoid huge payloads)
        preview_docs = [doc.page_content[:200] for doc in retrieved_docs]
        span.set_attribute(SpanAttributes.RETRIEVAL_DOCUMENTS, preview_docs)

    return {"context": retrieved_docs}


def generate(state: State):
    tracer = trace_api.get_tracer(__name__)
    # Start a span for the generate step, enriching the span with Open Inference attributes
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
        messages = prompt.invoke(
            {"question": state["question"], "context": docs_content}
        )
        response = llm.invoke(messages)

        # Store output
        span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(response.content))

    return {"answer": response.content}


graph_builder = StateGraph(State)
graph_builder.add_node(retrieve)
graph_builder.add_node(generate)
graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")

graph = graph_builder.compile()


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

        # Attach answer to root span
        root_span.set_attribute(SpanAttributes.OUTPUT_VALUE, result["answer"])

        st.write(result["answer"])

        with st.expander("Context"):
            st.write(result["context"])

# END full file