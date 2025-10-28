## Install

```bash
npm install --save @arizeai/openinference-instrumentation-langchain
```

## Setup

To load the LangChain instrumentation, manually instrument the `@langchain/core/callbacks/manager` module. The callbacks manager must be manually instrumented due to the non-traditional module structure in `@langchain/core`. Additional instrumentations can be registered as usual in the registerInstrumentations function.

```typescript
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { 
  LangChainInstrumentation 
} from "@arizeai/openinference-instrumentation-langchain";
import * as CallbackManagerModule from "@langchain/core/callbacks/manager";

const provider = new NodeTracerProvider();
provider.register();

const lcInstrumentation = new LangChainInstrumentation();
// LangChain must be manually instrumented as it doesn't have 
// a traditional module structure
lcInstrumentation.manuallyInstrument(CallbackManagerModule);
```


## Support

Instrumentation version >1.0.0 supports both attribute masking and context attribute propagation to spans.

## Resources

* [Example project](https://github.com/Arize-ai/openinference/blob/main/js/packages/openinference-instrumentation-langchain/examples)
* [OpenInference package](https://github.com/Arize-ai/openinference/blob/main/js/packages/openinference-instrumentation-langchain)