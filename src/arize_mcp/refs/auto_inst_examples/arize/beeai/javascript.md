
### Installation

```bash
npm install --save beeai-framework @arizeai/openinference-instrumentation-beeai \
    @opentelemetry/sdk-node @opentelemetry/instrumentation \
    @opentelemetry/exporter-trace-otlp-grpc @opentelemetry/resources \
    @opentelemetry/semantic-conventions @opentelemetry/api @grpc/grpc-js

# If your BeeAI agents use specific LLMs like OpenAI, install their SDKs too:
# npm install --save @openai/api-client # or equivalent openai package
```

### API Key Setup (for underlying LLMs)

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Setup Tracing

```javascript
import { NodeSDK, node } from "@opentelemetry/sdk-node";
import { Resource } from "@opentelemetry/resources";
import { SemanticResourceAttributes } from "@opentelemetry/semantic-conventions";
import { BeeAIInstrumentation } from "@arizeai/openinference-instrumentation-beeai";
import * as beeaiFramework from "beeai-framework"; // For manual instrumentation
import { Metadata } from "@grpc/grpc-js";
import { OTLPTraceExporter as GrpcOTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-grpc";
import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";

// For troubleshooting, set the log level (e.g., DiagLogLevel.DEBUG)
// diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

// --- Arize Exporter Configuration ---
const ARIZE_SPACE_KEY = "YOUR_SPACE_ID"; // Replace with your Arize Space ID
const ARIZE_API_KEY = "YOUR_API_KEY";   // Replace with your Arize API Key
const ARIZE_MODEL_ID = "my-beeai-app";   // Replace with your Arize Model ID
// const ARIZE_MODEL_VERSION = "1.0"; // Optional: specify a model version

const arizeMetadata = new Metadata();
arizeMetadata.set('space_id', ARIZE_SPACE_KEY);
arizeMetadata.set('api_key', ARIZE_API_KEY);

const arizeExporter = new GrpcOTLPTraceExporter({
  url: "https://otlp.arize.com/v1", // Arize OTLP gRPC endpoint
  metadata: arizeMetadata,
});

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: "beeai-service",
    "model_id": ARIZE_MODEL_ID,
    // "model_version": ARIZE_MODEL_VERSION, // Uncomment if using model version
  }),
  spanProcessors: [
    // Use BatchSpanProcessor for production environments
    new node.SimpleSpanProcessor(arizeExporter),
  ],
  instrumentations: [new BeeAIInstrumentation()],
});

async function initializeTracing() {
  try {
    await sdk.start();
    console.log("🐝 BeeAI OpenTelemetry SDK started successfully for Arize.");

    // Manually Patch BeeAgent if necessary (especially if using ES modules without commonjs interop)
    // This ensures the instrumentation can find and patch the BeeAI classes.
    const beeAIInstrumentation = sdk.getNodeInstrumentations().find(
        (instr) => instr.instrumentationName === '@arizeai/openinference-instrumentation-beeai'
    );
    if (beeAIInstrumentation) {
        console.log("🔧 Manually instrumenting BeeAI components...");
        (beeAIInstrumentation).manuallyInstrument(beeaiFramework);
        console.log("✅ BeeAI components manually instrumented.");
    } else {
        console.warn("Could not find BeeAIInstrumentation to manually instrument.");
    }

  } catch (error) {
    console.error("Failed to initialize BeeAI OpenTelemetry SDK for Arize:", error);
  }
}

initializeTracing();

// Ensure this instrumentation file is imported at the very start of your application
// e.g., in your main app file: require("./instrumentation"); or import "./instrumentation";
```

### Run BeeAI Example

```javascript
import "./instrumentation.js"; // This should be the first import

import { ReActAgent } from "beeai-framework/agents/react/agent";
import { TokenMemory } from "beeai-framework/memory/tokenMemory";
import { DuckDuckGoSearchTool } from "beeai-framework/tools/search/duckDuckGoSearch";
import { OpenMeteoTool } from "beeai-framework/tools/weather/openMeteo";
// Assuming you have an adapter for your chosen LLM, e.g., OpenAI
import { OpenAIChatModel } from "beeai-framework/adapters/openai/backend/chat"; 

async function main() {
  // Configure your LLM (ensure API keys are set if needed, e.g., via environment variables)
  const llm = new OpenAIChatModel(
    "gpt-4o", // Or your preferred model
    // {}, // Additional OpenAI config if needed
  );

  const agent = new ReActAgent({
    llm: llm,
    memory: new TokenMemory(),
    tools: [new DuckDuckGoSearchTool(), new OpenMeteoTool()],
  });

  try {
    const response = await agent.run({
      prompt: "What's the current weather in Amsterdam? And what about in San Francisco?",
    });
    console.log(`Agent 🤖 : `, response.result.text);
  } catch (error) {
    console.error("Error running BeeAI agent:", error);
  }
}

main();
```

