

### Installation

```bash

npm install @opentelemetry/exporter-trace-otlp-grpc @grpc/grpc-js

```

### Setup Tracing
```typescript

import { registerInstrumentations } from "@opentelemetry/instrumentation";
import { 
  OpenAIInstrumentation 
} from "@arizeai/openinference-instrumentation-openai";
import { ConsoleSpanExporter } from "@opentelemetry/sdk-trace-base";
import {
  NodeTracerProvider,
  SimpleSpanProcessor,
} from "@opentelemetry/sdk-trace-node";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { 
  OTLPTraceExporter as GrpcOTLPTraceExporter 
} from "@opentelemetry/exporter-trace-otlp-grpc"; // Arize specific
import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";
import { Metadata } from "@grpc/grpc-js"

// For troubleshooting, set the log level to DiagLogLevel.DEBUG
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

// Arize specific - Create metadata and add your headers
const metadata = new Metadata();

// Your Arize Space and API Keys, which can be found in the UI
metadata.set('space_id', 'your-space-id');
metadata.set('api_key', 'your-api-key');

const processor = new SimpleSpanProcessor(new ConsoleSpanExporter());
const otlpProcessor = new SimpleSpanProcessor(
  new GrpcOTLPTraceExporter({
    url: "https://otlp.arize.com/v1",
    metadata,
  })
);

const provider = new NodeTracerProvider({
  resource: resourceFromAttributes({
    // Arize specific - The name of a new or preexisting model you 
    // want to export spans to
    "model_id": "your-model-id",
    "model_version": "your-model-version"
  }),
  spanProcessors: [processor, otlpProcessor]
});

registerInstrumentations({
  instrumentations: [new OpenAIInstrumentation({})],
});

provider.register();

```