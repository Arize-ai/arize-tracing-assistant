### Installation

```bash
pip install arize-otel promptflow
```

### Launch Phoenix

```python
import os
from arize.otel import register, Endpoint
from opentelemetry.sdk.environment_variables import OTEL_EXPORTER_OTLP_ENDPOINT
from promptflow.tracing._start_trace import setup_exporter_from_environ
```

### Setup Open Telemetry

```python
tracer_provider = register(
    space_id = "your-space-id", # in app space settings page
    api_key = "your-api-key", # in app space settings page
    project_name = "your-project-name", # name this to whatever you would like
)

os.environ[OTEL_EXPORTER_OTLP_ENDPOINT] = Endpoint.ARIZE
setup_exporter_from_environ()
```


