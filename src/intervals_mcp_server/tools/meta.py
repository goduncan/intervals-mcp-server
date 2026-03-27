"""
Metadata tools for the Intervals.icu MCP server.
"""

import json

from intervals_mcp_server.mcp_instance import mcp  # noqa: F401
from intervals_mcp_server.utils.metadata import PACKAGE_NAME, get_package_version
from intervals_mcp_server.utils.server_info import get_server_info_payload


@mcp.tool()
async def get_server_version() -> str:
    """Get the MCP server version."""
    return f"{PACKAGE_NAME} {get_package_version()}"


@mcp.tool()
async def get_server_info() -> str:
    """Get MCP server metadata and configuration diagnostics."""
    payload = get_server_info_payload(
        host=mcp.settings.host,
        port=mcp.settings.port,
        sse_path=mcp.settings.sse_path,
        message_path=mcp.settings.message_path,
        streamable_http_path=mcp.settings.streamable_http_path,
    )
    return json.dumps(payload, indent=2, sort_keys=True)
