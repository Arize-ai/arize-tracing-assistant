from .arize_mcp import mcp
from .version import __version__


def main():
    print(f"Starting Arize MCP tracing assistant. Version {__version__}")
    mcp.run(transport="stdio")
