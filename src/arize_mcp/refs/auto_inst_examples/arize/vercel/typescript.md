### Installation

```bash
npm install --save @arizeai/openinference-vercel
```

### Installation

```bash
npm i @opentelemetry/api @vercel/otel @opentelemetry/exporter-trace-otlp-proto @arizeai/openinference-semantic-conventions
```

### Usage

```typescript
import { registerOTel } from "@vercel/otel";
import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";
import {
  isOpenInferenceSpan,
  OpenInferenceSimpleSpanProcessor,
} from "@arizeai/openinference-vercel";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { SEMRESATTRS_PROJECT_NAME } from "@arizeai/openinference-semantic-conventions";

// For troubleshooting, set the log level to DiagLogLevel.DEBUG
// This is not required and should not be added in a production setting
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

export function register() {
  registerOTel({
    serviceName: "phoenix-next-app",
    attributes: {
      // This is not required but it will allow you to send traces to a specific 
      // project in phoenix
      [SEMRESATTRS_PROJECT_NAME]: "your-next-app",
    },
    spanProcessors: [
      new OpenInferenceSimpleSpanProcessor({
        exporter: new OTLPTraceExporter({
          headers: {
            // API key if you're sending it to Phoenix
            api_key: process.env["PHOENIX_API_KEY"],
          },
          url:
            process.env["PHOENIX_COLLECTOR_ENDPOINT"] ||
            "https://app.phoenix.arize.com/v1/traces",
        }),
        spanFilter: (span) => {
          // Only export spans that are OpenInference to remove non-generative spans
          // This should be removed if you want to export all spans
          return isOpenInferenceSpan(span);
        },
      }),
    ],
  });
}
```

### Usage

```typescript
const result = await generateText({
  model: openai("gpt-4-turbo"),
  prompt: "Write a short story about a cat.",
  experimental_telemetry: { isEnabled: true },
});
```

