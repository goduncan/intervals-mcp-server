"""Tests for the guide resource."""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("API_KEY", "test")
os.environ.setdefault("ATHLETE_ID", "i1")

from intervals_mcp_server.resources.guide import USAGE_GUIDE, coaching_context_protocol  # noqa: E402


def test_guide_resource_returns_usage_guide():
    """The guide resource should return the static usage guide."""
    assert coaching_context_protocol() == USAGE_GUIDE


def test_guide_mentions_new_tools():
    """The guide should document the coaching-oriented tooling."""
    assert "get_training_summary" in USAGE_GUIDE
    assert "get_athlete_zones" in USAGE_GUIDE
    assert "get_athlete_power_curves" in USAGE_GUIDE
