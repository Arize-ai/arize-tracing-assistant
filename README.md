
<p align="left">
    <a target="_blank" href="https://arize.com" style="background:none">
        <img alt="arize banner" src="https://storage.googleapis.com/arize-assets/arize-logo-white.jpg"  width="300"></img>
</p>

# Arize Tracing Assistant
<a target="_blank" href="https://github.com/Arize-ai/arize/blob/main/sdk/python/arize-tracing-assistant/LICENSE">
    <img src="https://img.shields.io/pypi/l/arize-otel">
</a>
<img src="https://badge.mcpx.dev?status=on" title="MCP Enabled"/>
<a href="https://cursor.com/en/install-mcp?name=arize-tracing-assistant&config=eyJjb21tYW5kIjoidXZ4IGFyaXplLXRyYWNpbmctYXNzaXN0YW50QGxhdGVzdCIsImVudiI6e319"><img src="https://cursor.com/deeplink/mcp-install-dark.svg" alt="Add Arize tracing assistant MCP server to Cursor" height=20 /></a>
    
An MCP server that provides with docs and support to instrument your AI application with Arize AX.

## Overview

This MCP server provides your LLM with docs and examples to instrument your AI apps with Arize AX. It also provides with access to Arize support.
Connect it to your IDE or LLM and get curated tracing examples, best practices and Arize support!


## Installation

### Install uv

Make sure **uv** - the fast Python package manager - is installed on your system. Installation instructions: [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer).

- On macOS:
  ```bash
  pip install uv
  ```
  or

  ```bash
  brew install uv
  ```

- On Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | less
  ```
- On Windows:
  ```powershell
  powershell -c "irm https://astral.sh/uv/install.ps1 | more"
  ```

### IDE integration

#### [Antigravity](https://antigravity.google/)

1. Open the MCP Store panel within the "..." dropdown at the top of the editor's side panel.
2. Type "Arize" in the search and click Install.

OR

1. To Install as a Custom MCP Server, Click on "Manage MCP Servers"
2. Click on "View raw config"
3. Add the following code to your mcp_config.json:

```json
  "mcpServers": {
    "arize-tracing-assistant": {
      "command": "uvx",
      "args": [
      "arize-tracing-assistant@latest"
    ]
    }
  }
```

#### Cursor

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=arize-tracing-assistant&config=eyJjb21tYW5kIjoidXZ4IGFyaXplLXRyYWNpbmctYXNzaXN0YW50QGxhdGVzdCIsImVudiI6e319)

1. Go to Cursor Settings > MCP.
2. Click "Add new global MCP server" and add the server to your config JSON.
3. Remove the `env` section if you don't have access to RunLLM.

Example config:

```json
"arize-tracing-assistant": {
  "command": "uvx",
  "args": [
    "arize-tracing-assistant@latest"
  ]
}
```

---

#### Claude Desktop

1. Go to Claude Desktop Settings.
2. In Developer > Edit Config and add this to your config JSON:

```json
"arize-tracing-assistant": {
  "command": "/Users/myuser/miniconda3/bin/uvx",
  "args": [
   "arize-tracing-assistant@latest"
  ]
}
```

---

#### Manual MCP config

Add the following snippet to your MCP config file:

```json
  "mcpServers": {
    "arize-tracing-assistant": {
      "command": "uvx",
      "args": [
      "arize-tracing-assistant@latest"
    ]
    }
  }
```

### CLI Integration

#### Gemini CLI

Install using the Gemini CLI extension:

```bash
gemini extensions install https://github.com/Arize-ai/arize-tracing-assistant
```

## Usage

Once the MCP server is running, ask your IDE or LLM questions about tracing or general Arize support like...

- Instrument this app using Arize
- Can you use manual instrumentation so that I have more control over my traces?
- How can I redact sensitive information from my spans?
- Use decorators to have more control over the span attributes
- Can you make sure the context of this trace is propagated across these tool calls?
- Where can I find my Arize keys?

## Troubleshooting

- Make sure the JSON configs are perfectly formatted.
- Clear the **uv** cache with `uv cache clean` to force accessing the latest version.
- Make sure your `uv` command is pointing to the right location by running `which uv`, or simply use the full path.
- The server should start in the terminal just by running:

  ```bash
  uvx arize-tracing-assistant@latest
  ```

- Use the Anthropic MCP inspector by running:
  ```bash
  npx @modelcontextprotocol/inspector uvx arize-tracing-assistant@latest
  ```
