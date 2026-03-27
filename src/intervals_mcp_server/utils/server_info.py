"""
Server metadata and diagnostics helpers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from intervals_mcp_server.config import get_config
from intervals_mcp_server.server_setup import setup_transport
from intervals_mcp_server.utils.metadata import APP_NAME, get_build_revision, get_package_version

SUPPORTED_TOOLS = [
    "get_activities",
    "get_activity_details",
    "get_activity_intervals",
    "get_activity_streams",
    "get_events",
    "get_event_by_id",
    "delete_event",
    "delete_events_by_date_range",
    "add_or_update_event",
    "get_wellness_data",
    "get_custom_items",
    "get_custom_item_by_id",
    "create_custom_item",
    "update_custom_item",
    "delete_custom_item",
    "get_server_version",
    "get_server_info",
]


@dataclass
class ServerInfo:
    """Serializable server metadata for diagnostics tools."""

    name: str
    version: str
    revision: str
    transport: str
    api_base_url: str
    api_key_configured: bool
    athlete_id_configured: bool
    user_agent: str
    host: str
    port: int
    sse_path: str
    message_path: str
    streamable_http_path: str
    tools: list[str]


def get_server_info_payload(
    *,
    host: str,
    port: int,
    sse_path: str,
    message_path: str,
    streamable_http_path: str,
) -> dict[str, str | int | bool | list[str]]:
    """Build a serializable server info payload for diagnostics tools."""
    config = get_config()
    info = ServerInfo(
        name=APP_NAME,
        version=get_package_version(),
        revision=get_build_revision(),
        transport=setup_transport().value,
        api_base_url=config.intervals_api_base_url,
        api_key_configured=bool(config.api_key),
        athlete_id_configured=bool(config.athlete_id),
        user_agent=config.user_agent,
        host=host,
        port=port,
        sse_path=sse_path,
        message_path=message_path,
        streamable_http_path=streamable_http_path,
        tools=SUPPORTED_TOOLS,
    )
    return asdict(info)
