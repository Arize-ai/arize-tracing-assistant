# Arize Tracing Documentation - TypeScript/JavaScript

This comprehensive guide covers OpenTelemetry tracing for TypeScript/JavaScript applications with Arize, consolidating all essential information for LLM observability.

## Index
1. Installation & Setup
2. Auto-Instrumentation Catalogue
3. Auto-Instrumentation with Context Helpers (hybrid)
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
npm install @opentelemetry/sdk-node \
            @opentelemetry/instrumentation \
            @opentelemetry/exporter-trace-otlp-grpc \
            @opentelemetry/resources \
            @grpc/grpc-js \
            @arizeai/openinference-semantic-conventions
```

### Creating the Instrumentation File

Create an `instrumentation.ts` (or `.js`) file that should be imported first when your service starts:

```typescript
import { NodeSDK } from "@opentelemetry/sdk-node";
import { Resource } from "@opentelemetry/resources";
import { SEMRESATTRS_PROJECT_NAME } from "@arizeai/openinference-semantic-conventions";
import { OTLPTraceExporter as GrpcOTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";
import { Metadata } from "@grpc/grpc-js";

// Optional: Enable debug logging
// diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

// Arize exporter configuration
const metadata = new Metadata();
metadata.set("space_id", process.env.ARIZE_SPACE_ID || "<ARIZE_SPACE_ID>");
metadata.set("api_key", process.env.ARIZE_API_KEY || "<ARIZE_API_KEY>");

const arizeExporter = new GrpcOTLPTraceExporter({
    url: "https://otlp.arize.com/v1",
    metadata,
});

// SDK setup
const sdk = new NodeSDK({
    resource: new Resource({
        [SEMRESATTRS_PROJECT_NAME]: process.env.ARIZE_PROJECT_NAME || "my-llm-app",
    }),
    spanProcessorOptions: {
        exporter: arizeExporter,
    },
});

sdk.start()
    .then(() => console.log("📡 OpenTelemetry initialized - sending traces to Arize"))
    .catch((err) => console.error("Failed to start OpenTelemetry SDK", err));
```

### Loading the Instrumentation
```bash
# Using Node.js import flag
node --import ./instrumentation.js dist/index.js

# Or use require at the top of your entry file
require('./instrumentation');
```

### Advanced Configuration with Multiple Exporters
```typescript
import { ConsoleSpanExporter, BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";

// Create tracer provider with custom configuration
const provider = new NodeTracerProvider({
    resource: new Resource({
        "model_id": "your-model-name",
        "model_version": "v1.0",
        [SEMRESATTRS_PROJECT_NAME]: "my-llm-app"
    }),
});

// Add multiple span processors
provider.addSpanProcessor(new BatchSpanProcessor(new ConsoleSpanExporter()));
provider.addSpanProcessor(new BatchSpanProcessor(arizeExporter));

provider.register();
```

---

## 2. Auto-Instrumentation Catalogue
[SECTION:AUTO]

### Available Instrumentors

```bash
# Example: OpenAI
npm install @arizeai/openinference-instrumentation-openai
```

Available frameworks include: OpenAI, LangChain, Vercel AI SDK, and Bee AI. Simply replace `openai` in the package name with your framework of choice.

### Basic Auto-Instrumentation
```typescript
import { OpenAIInstrumentation } from "@arizeai/openinference-instrumentation-openai";
import { registerInstrumentations } from "@opentelemetry/instrumentation";

registerInstrumentations({
    instrumentations: [new OpenAIInstrumentation()],
});

// Your OpenAI calls now automatically create spans
```

### Multiple Instrumentations
```typescript
import { OpenAIInstrumentation } from "@arizeai/openinference-instrumentation-openai";
import { LangChainInstrumentation } from "@arizeai/openinference-instrumentation-langchain";

registerInstrumentations({
    instrumentations: [
        new OpenAIInstrumentation(),
        new LangChainInstrumentation(),
    ],
});
```

---

## 3. Auto-Instrumentation with Context Helpers and Decorators
[SECTION:DECORATORS]

### 3.1 Enriching Auto-Instrumented Spans
```typescript
import { trace } from "@opentelemetry/api";

// Get current span created by auto-instrumentation
const currentSpan = trace.getActiveSpan();

if (currentSpan) {
    // Add custom attributes
    currentSpan.setAttribute("operation.value", 1);
    currentSpan.setAttribute("operation.name", "Saying hello!");
    currentSpan.setAttribute("operation.other-stuff", [1, 2, 3]);
}
```

### 3.2 OpenInference Semantic Attributes
```typescript
import { trace } from "@opentelemetry/api";
import {
    SemanticConventions as SC,
    MessageAttributes,
} from "@arizeai/openinference-semantic-conventions";

const span = trace.getActiveSpan();
if (span) {
    span.setAttribute(SC.OUTPUT_VALUE, response);
    
    // Populate output messages table
    span.setAttribute(
        `${SC.LLM_OUTPUT_MESSAGES}.0.${MessageAttributes.MESSAGE_ROLE}`,
        "assistant"
    );
    span.setAttribute(
        `${SC.LLM_OUTPUT_MESSAGES}.0.${MessageAttributes.MESSAGE_CONTENT}`,
        response
    );
}
```

### 3.3 Context Propagation Helpers
```typescript
import { context } from "@opentelemetry/api";
import {
    setMetadata,
    setTags,
    setPromptTemplate,
    setAttributes,
    getAttributesFromContext
} from "@arizeai/openinference-core";

// Metadata propagation
context.with(setMetadata(context.active(), { run_id: "abc-123", env: "prod" }), () => {
    // All child spans inherit this metadata
    openai.chat.completions.create(...);
});

// Tags propagation
context.with(setTags(context.active(), ["rag", "retrieval"]), () => {
    // All child spans inherit these tags
});

// Prompt template propagation
context.with(
    setPromptTemplate(context.active(), {
        template: "Describe the weather in {{city}}",
        variables: { city: "Johannesburg" },
        version: "v1.0",
    }),
    () => {
        // Template info attached to spans
    }
);

// Combined attributes using low-level helper
context.with(
    setAttributes(context.active(), {
        "session.id": "sess-42",
        "user.id": "user-007"
    }),
    () => {
        // All attributes propagate to child spans
    }
);

// Retrieve context attributes in manual spans
const tracer = trace.getTracer("example");
tracer.startActiveSpan("manual", (span) => {
    span.setAttributes(getAttributesFromContext(context.active()));
    span.end();
});
```

### 3.4 OpenInference Decorators (Python reference)
**Note: TypeScript doesn't have direct decorator support like Python. Here's the Python pattern for reference:**

```python
# Python decorator pattern for reference
@tracer.chain
def process_request(input: str) -> str:
    return "processed"

@tracer.agent
def agent_task(query: str) -> str:
    return "agent response"

@tracer.tool
def search_tool(query: str, limit: int) -> list:
    """Search tool description"""
    return ["result1", "result2"]
```

**TypeScript equivalent using wrapper functions:**
```typescript
// TypeScript wrapper pattern to achieve similar functionality
function wrapAsChain<T extends (...args: any[]) => any>(
    name: string,
    fn: T
): T {
    return ((...args: Parameters<T>) => {
        const tracer = trace.getTracer("app");
        return tracer.startActiveSpan(name, { kind: SpanKind.INTERNAL }, (span) => {
            span.setAttribute("openinference.span.kind", "CHAIN");
            span.setAttribute("input.value", JSON.stringify(args));
            
            try {
                const result = fn(...args);
                span.setAttribute("output.value", JSON.stringify(result));
                span.setStatus({ code: SpanStatusCode.OK });
                return result;
            } catch (error) {
                span.recordException(error as Error);
                span.setStatus({ code: SpanStatusCode.ERROR });
                throw error;
            } finally {
                span.end();
            }
        });
    }) as T;
}

// Usage
const processRequest = wrapAsChain("process-request", (input: string) => {
    return "processed: " + input;
});
```

### 3.5 Suppress Tracing (Python reference)
**Note: TypeScript doesn't have a built-in suppress_tracing context manager. Here's the Python version for reference:**

```python
# Python example
from openinference.instrumentation import suppress_tracing

with suppress_tracing():
    # No spans created here
    client.chat.completions.create(...)
```

---

## 4. Manual Instrumentation
[SECTION:MANUAL]

### 4.1 Basic Manual Spans
```typescript
import { trace, SpanStatusCode } from "@opentelemetry/api";

const tracer = trace.getTracer("my-app");

tracer.startActiveSpan("my-operation", (span) => {
    span.setAttribute("input.value", "user query");
    
    try {
        // Your logic here
        const result = processData();
        span.setAttribute("output.value", result);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
    } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR });
        throw error;
    } finally {
        span.end();
    }
});
```

### 4.2 Span Types with Attributes

#### LLM Spans
```typescript
import { trace, SpanKind } from "@opentelemetry/api";
import { SemanticConventions as SC } from "@arizeai/openinference-semantic-conventions";

const tracer = trace.getTracer("llm-service");

tracer.startActiveSpan("llm-call", { kind: SpanKind.CLIENT }, async (span) => {
    span.setAttribute("openinference.span.kind", "LLM");
    span.setAttribute(SC.LLM_MODEL_NAME, "gpt-4");
    
    // Set input messages
    messages.forEach((msg, idx) => {
        span.setAttribute(
            `${SC.LLM_INPUT_MESSAGES}.${idx}.message.role`,
            msg.role
        );
        span.setAttribute(
            `${SC.LLM_INPUT_MESSAGES}.${idx}.message.content`,
            msg.content
        );
    });
    
    try {
        // Make LLM call
        const response = await openai.chat.completions.create({
            model: "gpt-4",
            messages: messages
        });
        
        // Set output
        span.setAttribute(SC.OUTPUT_VALUE, response.choices[0].message.content);
        span.setAttribute(
            `${SC.LLM_OUTPUT_MESSAGES}.0.message.role`,
            "assistant"
        );
        span.setAttribute(
            `${SC.LLM_OUTPUT_MESSAGES}.0.message.content`,
            response.choices[0].message.content
        );
        
        // Token counts
        if (response.usage) {
            span.setAttribute(SC.LLM_TOKEN_COUNT_PROMPT, response.usage.prompt_tokens);
            span.setAttribute(SC.LLM_TOKEN_COUNT_COMPLETION, response.usage.completion_tokens);
            span.setAttribute(SC.LLM_TOKEN_COUNT_TOTAL, response.usage.total_tokens);
        }
        
        span.setStatus({ code: SpanStatusCode.OK });
        return response;
    } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR });
        throw error;
    } finally {
        span.end();
    }
});
```

#### Retriever Spans
```typescript
tracer.startActiveSpan("vector-search", { kind: SpanKind.CLIENT }, async (span) => {
    span.setAttribute("openinference.span.kind", "RETRIEVER");
    span.setAttribute(SC.INPUT_VALUE, queryText);
    
    try {
        const documents = await searchClient.search(queryText);
        
        documents.forEach((doc, i) => {
            span.setAttribute(`retrieval.documents.${i}.document.id`, doc.id);
            span.setAttribute(`retrieval.documents.${i}.document.score`, doc.score);
            span.setAttribute(`retrieval.documents.${i}.document.content`, doc.content);
            span.setAttribute(`retrieval.documents.${i}.document.metadata`, JSON.stringify(doc.metadata));
        });
        
        span.setStatus({ code: SpanStatusCode.OK });
        return documents;
    } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR });
        throw error;
    } finally {
        span.end();
    }
});
```

#### Tool Spans
```typescript
tracer.startActiveSpan("tool-execution", { kind: SpanKind.INTERNAL }, (span) => {
    span.setAttribute("openinference.span.kind", "TOOL");
    span.setAttribute("tool.name", toolName);
    span.setAttribute("tool.arguments", JSON.stringify(toolArgs));
    
    try {
        // Execute tool
        const result = toolFunction(toolArgs);
        
        span.setAttribute("tool.output", JSON.stringify(result));
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
    } catch (error) {
        span.recordException(error as Error);
        span.setStatus({ code: SpanStatusCode.ERROR });
        throw error;
    } finally {
        span.end();
    }
});
```

#### Embedding Spans (Python reference with TS adaptation)
**Python example for reference:**
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

**TypeScript adaptation:**
```typescript
tracer.startActiveSpan("generate-embeddings", async (span) => {
    span.setAttribute("openinference.span.kind", "EMBEDDING");
    span.setAttribute("embedding.model.name", "text-embedding-ada-002");
    
    const embeddings = await embeddingModel.embed(texts);
    
    texts.forEach((text, i) => {
        span.setAttribute(`embedding.embeddings.${i}.text`, text);
        span.setAttribute(`embedding.embeddings.${i}.vector`, JSON.stringify(embeddings[i]));
    });
    
    span.end();
});
```

#### Reranker Spans (Python reference with TS adaptation)
**Python example for reference:**
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

**TypeScript adaptation:**
```typescript
tracer.startActiveSpan("rerank-documents", async (span) => {
    span.setAttribute("openinference.span.kind", "RERANKER");
    span.setAttribute("reranker.query", query);
    span.setAttribute("reranker.model_name", "cross-encoder/ms-marco-MiniLM-L-12-v2");
    span.setAttribute("reranker.top_k", topK);
    span.setAttribute("reranker.input_documents", JSON.stringify(inputDocs));
    
    const rerankedDocs = await reranker.rerank(query, inputDocs, topK);
    
    span.setAttribute("reranker.output_documents", JSON.stringify(rerankedDocs));
    span.end();
});
```

### 4.3 General Span Attributes
```typescript
// Common attributes for any span type
span.setAttribute("input.value", "<INPUT>");
span.setAttribute("input.mime_type", "text/plain");
span.setAttribute("output.value", "<OUTPUT>");
span.setAttribute("output.mime_type", "text/plain");
span.setAttribute("tag.tags", JSON.stringify(["tag1", "tag2"]));
span.setAttribute("metadata", JSON.stringify({ key: "value" }));
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
```typescript
import { 
    SemanticConventions as SC 
} from "@arizeai/openinference-semantic-conventions";

// Common patterns
"openinference.span.kind"        // Span type
SC.INPUT_VALUE                   // Input data
SC.OUTPUT_VALUE                  // Output data
SC.LLM_MODEL_NAME               // Model identifier
SC.LLM_TOKEN_COUNT_PROMPT       // Prompt tokens
SC.LLM_TOKEN_COUNT_COMPLETION   // Completion tokens
SC.LLM_TOKEN_COUNT_TOTAL        // Total tokens
SC.LLM_INPUT_MESSAGES           // Chat messages
SC.LLM_OUTPUT_MESSAGES          // Output messages
```

---

## 6. Events, Exceptions & Status Handling
[SECTION:EVENTS]

### 6.1 Adding Events
```typescript
const span = trace.getActiveSpan();

if (span) {
    // Log events during execution
    span.addEvent("Starting LLM call");
    const response = await llm.complete(prompt);
    span.addEvent("LLM call completed", {
        "response.length": response.length,
        "model.temperature": 0.7
    });
}
```

### 6.2 Setting Span Status
```typescript
import { SpanStatusCode } from "@opentelemetry/api";

try {
    const result = await riskyOperation();
    span.setStatus({ code: SpanStatusCode.OK });
} catch (error) {
    span.setStatus({ 
        code: SpanStatusCode.ERROR, 
        message: error.message 
    });
}
```

### 6.3 Recording Exceptions
```typescript
try {
    const result = await processData();
} catch (error) {
    span.setStatus({ code: SpanStatusCode.ERROR });
    span.recordException(error as Error);
    // Exception details are preserved in span
    throw error;
}
```

### 6.4 Complete Error Handling Pattern
```typescript
tracer.startActiveSpan("data-processing", async (span) => {
    span.addEvent("Processing started");
    
    try {
        // Risky operation
        const data = await fetchExternalData();
        span.addEvent("Data fetched successfully");
        
        const result = await transformData(data);
        span.setAttribute("output.value", result);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
        
    } catch (error) {
        if (error instanceof ConnectionError) {
            span.recordException(error);
            span.setStatus({ 
                code: SpanStatusCode.ERROR, 
                message: "Failed to fetch data" 
            });
            span.addEvent("Connection failed", { "retry.attempts": 3 });
        } else {
            span.recordException(error as Error);
            span.setStatus({ code: SpanStatusCode.ERROR });
        }
        throw error;
    } finally {
        span.end();
    }
});
```

---

## 7. Context Propagation Recipes
[SECTION:CONTEXT]

### 7.1 Async Context Propagation
```typescript
import { context, trace } from "@opentelemetry/api";

const tracer = trace.getTracer("async-example");

async function asyncOperation() {
    const span = trace.getActiveSpan();
    if (span) {
        span.setAttribute("async.operation", "processing");
        await new Promise(resolve => setTimeout(resolve, 1000));
        span.addEvent("Async operation completed");
    }
}

function mainOperation() {
    tracer.startActiveSpan("main", async (span) => {
        // Context automatically propagates to async functions
        await asyncOperation();
        span.end();
    });
}
```

### 7.2 Parallel Processing with Context
```typescript
async function processItem(item: any) {
    const span = trace.getActiveSpan();
    if (span) {
        span.setAttribute("item.id", item.id);
        // Process the item
        const result = await expensiveComputation(item);
        span.addEvent(`Processed item ${item.id}`);
        return result;
    }
}

async function parallelProcessing(items: any[]) {
    await tracer.startActiveSpan("parallel-batch", async (span) => {
        // Context propagates to all parallel operations
        const results = await Promise.all(
            items.map(item => processItem(item))
        );
        
        span.setAttribute("batch.size", items.length);
        span.end();
        return results;
    });
}
```

### 7.3 Cross-Service Propagation
```typescript
import { propagation, context } from "@opentelemetry/api";
import axios from "axios";

// Service A - Inject context into headers
async function callServiceB() {
    return tracer.startActiveSpan("call-service-b", async (span) => {
        const headers: Record<string, string> = {};
        
        // Inject trace context into headers
        propagation.inject(context.active(), headers);
        
        const response = await axios.get("http://service-b/api/endpoint", { headers });
        span.setAttribute("http.status_code", response.status);
        span.end();
        return response.data;
    });
}

// Service B - Extract context from headers
import express from "express";

const app = express();

app.get("/api/endpoint", (req, res) => {
    // Extract context from incoming request
    const extractedContext = propagation.extract(context.active(), req.headers);
    
    context.with(extractedContext, () => {
        tracer.startActiveSpan("process-request", (span) => {
            span.addEvent("Received request from Service A");
            // Process request with proper trace context
            const result = processBusinessLogic();
            span.end();
            res.json(result);
        });
    });
});
```

### 7.4 Manual Context Management (Python reference)
**Note: TypeScript/JavaScript handles context differently than Python. Here's the Python pattern for reference:**

```python
# Python manual context propagation
from opentelemetry.context import attach, detach, get_current

def with_current_context(func):
    """Decorator that preserves trace context"""
    def wrapper(*args, **kwargs):
        context = get_current()
        token = attach(context)
        try:
            return func(*args, **kwargs)
        finally:
            detach(token)
    return wrapper
```

**TypeScript uses automatic context propagation within the same async context:**
```typescript
// TypeScript automatically maintains context in async operations
async function backgroundTask(data: any) {
    const span = trace.getActiveSpan();
    if (span) {
        span.setAttribute("task.data", JSON.stringify(data));
    }
    // Task executes with proper context automatically
}
```

---

## 8. Prompt Templates & Variables
[SECTION:PROMPT]

### 8.1 Basic Prompt Template Instrumentation
```typescript
import { context } from "@opentelemetry/api";
import { setPromptTemplate } from "@arizeai/openinference-core";

const promptTemplate = "Please describe the weather forecast for {{city}} on {{date}}";
const promptVariables = { city: "Johannesburg", date: "July 11" };

context.with(
    setPromptTemplate(context.active(), {
        template: promptTemplate,
        variables: promptVariables,
        version: "v1.0",
    }),
    async () => {
        // Format the prompt
        const formattedPrompt = promptTemplate
            .replace("{{city}}", promptVariables.city)
            .replace("{{date}}", promptVariables.date);
        
        // Make LLM call - template info automatically attached to spans
        const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [{ role: "user", content: formattedPrompt }]
        });
    }
);
```

### 8.2 Template Versioning Pattern
```typescript
class PromptManager {
    private templates = {
        "v1.0": "Summarize this text: {{text}}",
        "v1.1": "Provide a concise summary of the following: {{text}}",
        "v2.0": "Create a {{style}} summary of: {{text}}"
    };
    
    async getPrompt(version: string, variables: Record<string, string>): Promise<string> {
        const template = this.templates[version];
        
        return context.with(
            setPromptTemplate(context.active(), {
                template,
                variables,
                version
            }),
            () => {
                // Simple template replacement
                return Object.entries(variables).reduce(
                    (acc, [key, value]) => acc.replace(`{{${key}}}`, value),
                    template
                );
            }
        );
    }
}

// Usage
const promptMgr = new PromptManager();
const prompt = await promptMgr.getPrompt("v2.0", { 
    text: document, 
    style: "technical" 
});
```

### 8.3 Dynamic Template Selection
```typescript
async function generateResponse(
    queryType: "question" | "translation" | "summary",
    variables: Record<string, string>
) {
    const templates = {
        question: "Answer this question: {{question}}",
        translation: "Translate to {{targetLang}}: {{text}}",
        summary: "Summarize in {{maxWords}} words: {{content}}"
    };
    
    const template = templates[queryType];
    
    return context.with(
        setPromptTemplate(context.active(), {
            template,
            variables,
            version: "dynamic"
        }),
        async () => {
            const prompt = Object.entries(variables).reduce(
                (acc, [key, value]) => acc.replace(`{{${key}}}`, value),
                template
            );
            return await llm.complete(prompt);
        }
    );
}
```

---

## 9. Masking, Redaction & Span Filtering
[SECTION:MASK]

### 9.1 Environment Variable Masking
```typescript
// Set these before starting your application
process.env.OPENINFERENCE_HIDE_INPUTS = "false";
process.env.OPENINFERENCE_HIDE_OUTPUTS = "false";
process.env.OPENINFERENCE_HIDE_INPUT_MESSAGES = "false";
process.env.OPENINFERENCE_HIDE_OUTPUT_MESSAGES = "false";
process.env.OPENINFERENCE_HIDE_INPUT_IMAGES = "true";
process.env.OPENINFERENCE_HIDE_INPUT_TEXT = "false";
process.env.OPENINFERENCE_HIDE_OUTPUT_TEXT = "false";
process.env.OPENINFERENCE_HIDE_EMBEDDING_VECTORS = "true";
process.env.OPENINFERENCE_BASE64_IMAGE_MAX_LENGTH = "1000";
```

### 9.2 TraceConfig Masking
```typescript
import { OpenAIInstrumentation } from "@arizeai/openinference-instrumentation-openai";

const traceConfig = {
    hideInputs: false,
    hideOutputs: false,
    hideInputMessages: false,
    hideOutputMessages: false,
    hideInputImages: true,           // Hide image data
    hideInputText: false,
    hideOutputText: false,
    hideEmbeddingVectors: true,      // Hide large vectors
    base64ImageMaxLength: 1000,      // Truncate images
};

const instrumentation = new OpenAIInstrumentation({ traceConfig });
```

### 9.3 Custom PII Redaction (Python reference)
**Note: TypeScript span processors work differently. Here's the Python pattern for reference:**

```python
# Python PII Redaction Processor
import re
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan

class PIIRedactingSpanProcessor(SpanProcessor):
    def __init__(self, exporter):
        self._exporter = exporter
        self._patterns = {
            'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
            'phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        }
    
    def _redact_string(self, value: str) -> str:
        for name, pattern in self._patterns.items():
            value = pattern.sub(f'[REDACTED_{name.upper()}]', value)
        return value
```

**TypeScript adaptation using a custom span processor:**
```typescript
import { SpanProcessor, ReadableSpan, Span } from "@opentelemetry/sdk-trace-base";
import { Context } from "@opentelemetry/api";

class PIIRedactingSpanProcessor implements SpanProcessor {
    private patterns = {
        email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
        phone: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,
        ssn: /\b\d{3}-\d{2}-\d{4}\b/g,
    };
    
    constructor(private exporter: SpanExporter) {}
    
    private redactString(value: string): string {
        let result = value;
        for (const [name, pattern] of Object.entries(this.patterns)) {
            result = result.replace(pattern, `[REDACTED_${name.toUpperCase()}]`);
        }
        return result;
    }
    
    private redactValue(value: any): any {
        if (typeof value === 'string') {
            return this.redactString(value);
        } else if (Array.isArray(value)) {
            return value.map(item => this.redactValue(item));
        } else if (typeof value === 'object' && value !== null) {
            const result: any = {};
            for (const [key, val] of Object.entries(value)) {
                result[key] = this.redactValue(val);
            }
            return result;
        }
        return value;
    }
    
    onStart(span: Span, parentContext: Context): void {
        // Not needed for redaction
    }
    
    onEnd(span: ReadableSpan): void {
        // Create redacted copy of attributes
        const redactedAttributes: Record<string, any> = {};
        for (const [key, value] of Object.entries(span.attributes || {})) {
            redactedAttributes[key] = this.redactValue(value);
        }
        
        // Export with redacted attributes
        // Note: Implementation depends on your exporter
        this.exporter.export([span], () => {});
    }
    
    shutdown(): Promise<void> {
        return this.exporter.shutdown();
    }
    
    forceFlush(): Promise<void> {
        return this.exporter.forceFlush();
    }
}
```

### 9.4 Custom Sampling (Python reference)
**Note: Here's the Python custom sampler pattern for reference:**

```python
# Python custom sampler
from opentelemetry.sdk.trace.sampling import Sampler, SamplingResult, Decision

class ConditionalSampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, kind, attributes, links):
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
```

---

## 10. Offline Evaluations & Experiments
[SECTION:EVAL]

### 10.1 Export Traces for Evaluation (Python reference)
**Note: Trace export and evaluation is primarily done in Python. Here's the reference:**

```python
# Python code for exporting traces
import os
from datetime import datetime
from arize.exporter import ArizeExportClient
from arize.utils.types import Environments

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

### 10.2 Run Custom Evaluations (Python reference)
```python
# Python evaluation code
from phoenix.evals import OpenAIModel, llm_classify

eval_model = OpenAIModel(
    model="gpt-4o",
    temperature=0,
    api_key=os.environ["OPENAI_API_KEY"]
)

EVAL_TEMPLATE = '''
You are evaluating response quality.
[Question]: {input}
[Response]: {output}

Rate the response as either "good", "acceptable", or "poor".
'''

evals_df = llm_classify(
    dataframe=traces_df,
    template=EVAL_TEMPLATE,
    model=eval_model,
    rails=["good", "acceptable", "poor"]
)
```

### 10.3 TypeScript Evaluation Pattern
While evaluation is typically done in Python, you can create evaluation spans in TypeScript:

```typescript
async function evaluateResponse(input: string, output: string): Promise<{
    quality: string;
    score: number;
    explanation: string;
}> {
    return tracer.startActiveSpan("evaluate-response", async (span) => {
        span.setAttribute("openinference.span.kind", "EVALUATOR");
        span.setAttribute("input.value", input);
        span.setAttribute("output.value", output);
        
        try {
            // Call evaluation service
            const evaluation = await evaluationService.evaluate({
                input,
                output,
                criteria: ["accuracy", "completeness", "clarity"]
            });
            
            span.setAttribute("eval.quality.label", evaluation.quality);
            span.setAttribute("eval.quality.score", evaluation.score);
            span.setAttribute("eval.quality.explanation", evaluation.explanation);
            
            span.setStatus({ code: SpanStatusCode.OK });
            return evaluation;
        } catch (error) {
            span.recordException(error as Error);
            span.setStatus({ code: SpanStatusCode.ERROR });
            throw error;
        } finally {
            span.end();
        }
    });
}
```
