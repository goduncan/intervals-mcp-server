"""
Metadata tools for the Intervals.icu MCP server.
"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib

from intervals_mcp_server.mcp_instance import mcp  # noqa: F401


def _get_package_version() -> str:
    """Return the package version, even when running directly from source."""
    try:
        return version("intervals-mcp-server")
    except PackageNotFoundError:
        pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
        with pyproject_path.open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)
        return str(pyproject["project"]["version"])


@mcp.tool()
async def get_server_version() -> str:
    """Get the MCP server version."""
    return f"intervals-mcp-server {_get_package_version()}"
