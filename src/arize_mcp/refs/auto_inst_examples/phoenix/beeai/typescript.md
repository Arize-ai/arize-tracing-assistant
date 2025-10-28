### Installation

```bash
npm install --save @arizeai/openinference-instrumentation-beeai beeai-framework

npm install --save @opentelemetry/sdk-node @opentelemetry/exporter-trace-otlp-http @opentelemetry/semantic-conventions @arizeai/openinference-semantic-conventions
```

### Usage

```typescript
// instrumentation.js
import { NodeSDK, node, resources } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { ATTR_SERVICE_NAME } from "@opentelemetry/semantic-conventions";
import { SEMRESATTRS_PROJECT_NAME } from "@arizeai/openinference-semantic-conventions";
import { BeeAIInstrumentation } from "@arizeai/openinference-instrumentation-beeai";
import * as beeaiFramework from "beeai-framework";

// Initialize Instrumentation Manually
const beeAIInstrumentation = new BeeAIInstrumentation();

const provider = new NodeSDK({
  resource: new resources.Resource({
    [ATTR_SERVICE_NAME]: "beeai",
    [SEMRESATTRS_PROJECT_NAME]: "beeai-project",
  }),
  spanProcessors: [
    new node.SimpleSpanProcessor(
      new OTLPTraceExporter({
        url: "http://localhost:6006/v1/traces",
      }),
    ),
  ],
  instrumentations: [beeAIInstrumentation],
});

await provider.start();

// Manually Patch BeeAgent (This is needed when the module is not loaded via require (commonjs))
console.log("🔧 Manually instrumenting BeeAgent...");
beeAIInstrumentation.manuallyInstrument(beeaiFramework);
console.log("✅ BeeAgent manually instrumented.");

// eslint-disable-next-line no-console
console.log("👀 OpenInference initialized");
```

### Usage

```typescript
import "./instrumentation";
import { BeeAgent } from "beeai-framework/agents/bee/agent";
import { TokenMemory } from "beeai-framework/memory/tokenMemory";
import { DuckDuckGoSearchTool } from "beeai-framework/tools/search/duckDuckGoSearch";
import { OpenMeteoTool } from "beeai-framework/tools/weather/openMeteo";
import { OllamaChatModel } from "beeai-framework/adapters/ollama/backend/chat";

const llm = new OllamaChatModel("llama3.1");
const agent = new BeeAgent({
  llm,
  memory: new TokenMemory(),
  tools: [new DuckDuckGoSearchTool(), new OpenMeteoTool()],
});

const response = await agent.run({
  prompt: "What's the current weather in Berlin?",
});

console.log(`Agent 🤖 : `, response.result.text);
```

