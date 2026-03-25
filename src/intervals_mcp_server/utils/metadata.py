"""
Metadata helpers for the Intervals.icu MCP server.
"""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import tomllib

PACKAGE_NAME = "intervals-mcp-server"
APP_NAME = "intervals-icu"


def get_package_version() -> str:
    """Return the installed package version or the source tree version."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
        with pyproject_path.open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)
        return str(pyproject["project"]["version"])


def get_user_agent() -> str:
    """Return a user agent string aligned with the package version."""
    return f"intervalsicu-mcp-server/{get_package_version()}"


def get_build_revision() -> str:
    """Return an optional build or git revision identifier if configured."""
    return (
        os.getenv("MCP_SERVER_GIT_SHA")
        or os.getenv("GIT_COMMIT_SHA")
        or os.getenv("SOURCE_VERSION")
        or "unknown"
    )
