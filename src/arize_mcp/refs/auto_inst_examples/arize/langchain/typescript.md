### Install (JS/TS)

```bash
npm install @arizeai/openinference-instrumentation-langchain @opentelemetry/exporter-trace-otlp-grpc @grpc/grpc-js @langchain/core @langchain/openai
```

### Setup Tracing (JS/TS)

```typescript
/* instrumentation.ts */
import { LangChainInstrumentation } from "@arizeai/openinference-instrumentation-langchain";
import { ConsoleSpanExporter } from "@opentelemetry/sdk-trace-base"; // Optional: for console logging
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-node";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { OTLPTraceExporter as GrpcOTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";
import { Metadata } from "@grpc/grpc-js";
import * as CallbackManagerModule from "@langchain/core/callbacks/manager"; // Critical for LangChain instrumentation

// For troubleshooting, set the log level to DiagLogLevel.DEBUG
// diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO); // Or DiagLogLevel.DEBUG

const spaceId = process.env.ARIZE_SPACE_ID || "YOUR_ARIZE_SPACE_ID";
const apiKey = process.env.ARIZE_API_KEY || "YOUR_ARIZE_API_KEY";
const projectName = process.env.ARIZE_PROJECT_NAME || "my-langchain-js-app";

// Arize specific: Create metadata for OTLP exporter headers
const metadata = new Metadata();
metadata.set('space_id', spaceId);
metadata.set('api_key', apiKey);

// Optional: Console exporter for local debugging
const consoleExporter = new ConsoleSpanExporter();
const consoleProcessor = new SimpleSpanProcessor(consoleExporter);

// Arize OTLP gRPC exporter
const otlpExporter = new GrpcOTLPTraceExporter({
  url: "https://otlp.arize.com/v1", // Arize OTLP endpoint
  metadata,
});
const otlpProcessor = new SimpleSpanProcessor(otlpExporter);

const provider = new NodeTracerProvider({
  resource: resourceFromAttributes({
    // Arize specific: Define the project for your traces
    "project_name": projectName,
    // You can add other resource attributes here if needed
  }),
  // Add spanProcessors: otlpProcessor for Arize, consoleProcessor for local logs
  spanProcessors: [otlpProcessor, consoleProcessor] 
});

// Register the LangChain instrumentation
const lcInstrumentation = new LangChainInstrumentation();
// LangChain must be manually instrumented as it doesn't have a traditional module structure
// that OpenTelemetry auto-instrumentation typically relies on.
// The CallbackManagerModule is what OpenInference hooks into.
lcInstrumentation.manuallyInstrument(CallbackManagerModule);

provider.register();

console.log(\`LangChain instrumented for Arize (JS/TS). Project: \${projectName}\`);

// Example of how to run your LangChain code (e.g., in your main app.ts or server.ts)
// import { ChatOpenAI } from "@langchain/openai";
// import { HumanMessage } from "@langchain/core/messages";

// async function main() {
//   if (!process.env.OPENAI_API_KEY) {
//     throw new Error("OPENAI_API_KEY environment variable is not set.");
//   }
//   const chat = new ChatOpenAI({ modelName: "gpt-3.5-turbo", temperature: 0 });
//   const response = await chat.invoke([
//     new HumanMessage("Hello, how are you today?"),
//   ]);
//   console.log(response);
// }
// main().catch(console.error);
```

### Native Thread Tracking (JS/TS)

```typescript
// Example:
// import { ChatOpenAI } from "@langchain/openai";

// const chatModel = new ChatOpenAI({
//   openAIApiKey: "YOUR_OPENAI_API_KEY",
//   modelName: "gpt-3.5-turbo",
// });

// async function runConversation() {
//   const threadId = "my-unique-thread-id-123";

//   // First message invocation
//   const response1 = await chatModel.invoke("Hello, how are you?", {
//     metadata: {
//       thread_id: threadId,
//     },
//   });
//   console.log("Response 1:", response1.content);

//   // Second message invocation
//   const response2 = await chatModel.invoke("What can you do?", {
//     metadata: {
//       thread_id: threadId,
//     },
//   });
//   console.log("Response 2:", response2.content);
// }
// runConversation().catch(console.error);
```

