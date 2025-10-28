# Phoenix Installation Guide

This guide provides instructions on how to install and launch Phoenix using various deployment methods.

## Command Line

### Launch Your Local Phoenix Instance:

```bash
pip install arize-phoenix
phoenix serve
```

For details on customizing a local terminal deployment, see [Terminal Setup](https://docs.arize.com/phoenix/setup/environments#terminal).

### Install Packages:

```bash
pip install arize-phoenix-otel
```

### Set Your Phoenix Endpoint:

```python
import os

os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"
```

## Notebook

### Install Packages:

```bash
pip install arize-phoenix
```

### Launch Phoenix:

```python
import phoenix as px
px.launch_app()
```

> **Note:** By default, notebook instances do not have persistent storage, so your traces will disappear after the notebook is closed. See [self-hosting](https://docs.arize.com/phoenix/self-hosting) or use one of the other deployment options to retain traces. 

## Phoenix Cloud

### Sign up for Phoenix:

Sign up for an Arize Phoenix account at [Phoenix Login](https://app.phoenix.arize.com/login).

### Install Packages:

```bash
pip install arize-phoenix-otel
```

### Set Your Phoenix Endpoint and API Key:

```python
import os

# Add Phoenix API Key for tracing
PHOENIX_API_KEY = "ADD YOUR API KEY"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"
```

Your **Phoenix API key** can be found in the Keys section of your [dashboard](https://app.phoenix.arize.com).

## Docker

### Pull Latest Phoenix Image from Docker Hub:

```bash
docker pull arizephoenix/phoenix:latest
```

### Run Your Containerized Instance:

```bash
docker run -p 6006:6006 arizephoenix/phoenix:latest
```

This will expose Phoenix on `localhost:6006`.

### Install Packages:

```bash
pip install arize-phoenix-otel
```

### Set Your Phoenix Endpoint:

```python
import os

os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"
```

For more info on using Phoenix with Docker, see [Docker](https://docs.arize.com/phoenix/self-hosting/deployment-options/docker).
