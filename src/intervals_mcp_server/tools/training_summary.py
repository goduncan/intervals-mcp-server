"""
Training summary MCP tool for Intervals.icu.

This module provides a compact training snapshot for a given date range by
aggregating athlete-summary, activities, and wellness data.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import set_if, strip_nulls
from intervals_mcp_server.utils.validation import (
    resolve_athlete_id,
    resolve_date_params,
    validate_date,
)

from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()


def _round1(value: Any) -> float | None:
    """Round a numeric value to one decimal place."""
    if value is None:
        return None
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def _round2(value: Any) -> float | None:
    """Round a numeric value to two decimal places."""
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _build_by_sport(categories: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Build a by-sport summary from athlete-summary categories."""
    result: dict[str, dict[str, Any]] = {}
    for cat in categories:
        name = cat.get("category")
        if not name:
            continue
        sport: dict[str, Any] = {
            "count": cat.get("count", 0),
            "tss": _round1(cat.get("training_load")),
            "duration_secs": cat.get("time", 0),
        }
        set_if(sport, "distance_m", cat.get("distance"), positive=True, transform=_round1)
        set_if(
            sport,
            "elevation_m",
            cat.get("total_elevation_gain"),
            positive=True,
            transform=_round1,
        )
        set_if(sport, "eftp_w", cat.get("eftp"), transform=_round1)
        set_if(sport, "eftp_w_kg", cat.get("eftpPerKg"), transform=_round1)
        result[name] = strip_nulls(sport)
    return result


def _build_period_totals(weeks: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate totals across all summary weeks."""
    sessions = 0
    duration = 0
    tss = 0.0
    srpe = 0.0
    distance = 0.0
    elevation = 0.0
    sport_agg: dict[str, dict[str, float]] = {}

    for week in weeks:
        sessions += week.get("count", 0)
        duration += week.get("time", 0)
        tss += week.get("training_load", 0) or 0
        srpe += week.get("srpe", 0) or 0
        distance += week.get("distance", 0) or 0
        elevation += week.get("total_elevation_gain", 0) or 0

        for cat in week.get("byCategory", []):
            name = cat.get("category")
            if not name:
                continue
            agg = sport_agg.setdefault(
                name,
                {
                    "count": 0.0,
                    "tss": 0.0,
                    "duration_secs": 0.0,
                    "distance_m": 0.0,
                    "elevation_m": 0.0,
                },
            )
            agg["count"] += cat.get("count", 0)
            agg["tss"] += cat.get("training_load", 0) or 0
            agg["duration_secs"] += cat.get("time", 0)
            agg["distance_m"] += cat.get("distance", 0) or 0
            agg["elevation_m"] += cat.get("total_elevation_gain", 0) or 0

    by_sport: dict[str, dict[str, Any]] = {}
    for name, agg in sport_agg.items():
        sport: dict[str, Any] = {
            "count": int(agg["count"]),
            "tss": _round1(agg["tss"]),
            "duration_secs": int(agg["duration_secs"]),
        }
        set_if(sport, "distance_m", agg["distance_m"], positive=True, transform=_round1)
        set_if(sport, "elevation_m", agg["elevation_m"], positive=True, transform=_round1)
        by_sport[name] = strip_nulls(sport)

    totals: dict[str, Any] = {
        "sessions": sessions,
        "duration_secs": duration,
        "tss": _round1(tss),
        "srpe": _round1(srpe),
    }
    set_if(totals, "distance_m", distance, positive=True, transform=_round1)
    set_if(totals, "elevation_m", elevation, positive=True, transform=_round1)
    if by_sport:
        totals["by_sport"] = by_sport
    return strip_nulls(totals)


def _compute_weekly_compliance(
    activities: list[dict[str, Any]],
    week_start: str,
    week_end: str,
) -> int | None:
    """Compute average compliance for activities in a week."""
    start = datetime.strptime(week_start, "%Y-%m-%d").date()
    end = datetime.strptime(week_end, "%Y-%m-%d").date()

    compliance_values: list[float] = []
    for activity in activities:
        date_str = activity.get("start_date_local", "")
        if not date_str:
            continue
        try:
            act_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue
        if start <= act_date <= end:
            comp = activity.get("compliance")
            if comp is not None:
                try:
                    compliance_values.append(float(comp))
                except (TypeError, ValueError):
                    pass

    if not compliance_values:
        return None
    return round(sum(compliance_values) / len(compliance_values))


def _compute_weekly_wellness(
    wellness_data: list[dict[str, Any]],
    week_start: str,
    week_end: str,
) -> dict[str, float]:
    """Average wellness metrics for days in the given week."""
    start = datetime.strptime(week_start, "%Y-%m-%d").date()
    end = datetime.strptime(week_end, "%Y-%m-%d").date()
    field_map = {
        "hrvRMSSD": "hrv",
        "restingHR": "resting_hr_bpm",
        "sleepSecs": "_sleep_secs",
        "fatigue": "fatigue",
        "mood": "mood",
    }

    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for entry in wellness_data:
        date_str = entry.get("id") or entry.get("date", "")
        if not date_str:
            continue
        try:
            entry_date = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            continue
        if start <= entry_date <= end:
            for api_field, out_key in field_map.items():
                value = entry.get(api_field)
                if value is not None:
                    try:
                        sums[out_key] = sums.get(out_key, 0.0) + float(value)
                        counts[out_key] = counts.get(out_key, 0) + 1
                    except (TypeError, ValueError):
                        pass

    result: dict[str, float] = {}
    for key, total in sums.items():
        avg = total / counts[key]
        if key == "_sleep_secs":
            result["sleep_hrs"] = round(avg / 3600, 1)
        else:
            result[key] = round(avg, 1)
    return result


def _build_weeks(
    summary_weeks: list[dict[str, Any]],
    activities: list[dict[str, Any]],
    wellness_data: list[dict[str, Any]],
    today: datetime,
) -> list[dict[str, Any]]:
    """Build the per-week breakdown."""
    result: list[dict[str, Any]] = []
    today_date = today.date()

    for week in summary_weeks:
        date_str = week.get("date", "")
        if not date_str:
            continue

        week_start_dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        week_end_dt = week_start_dt + timedelta(days=6)
        week_start = date_str
        week_end = week_end_dt.strftime("%Y-%m-%d")

        row: dict[str, Any] = {
            "week_start": week_start,
            "week_end": week_end,
            "partial": week_end_dt > today_date,
            "tss": _round1(week.get("training_load")),
            "srpe": _round1(week.get("srpe")),
            "duration_secs": week.get("time", 0),
            "sessions": week.get("count", 0),
            "ramp_rate": _round1(week.get("rampRate")),
            "ctl": _round1(week.get("fitness")),
            "atl": _round1(week.get("fatigue")),
            "tsb": _round1(week.get("form")),
        }

        compliance = _compute_weekly_compliance(activities, week_start, week_end)
        if compliance is not None:
            row["compliance_pct"] = compliance

        by_cat = week.get("byCategory", [])
        if by_cat:
            row["by_sport"] = _build_by_sport(by_cat)

        wellness = _compute_weekly_wellness(wellness_data, week_start, week_end)
        if wellness:
            row["wellness"] = wellness

        result.append(strip_nulls(row))

    return result


def _normalise_wellness(raw: Any) -> list[dict[str, Any]]:
    """Normalise wellness API responses to a flat list of dicts."""
    if isinstance(raw, list):
        return [entry for entry in raw if isinstance(entry, dict)]
    if isinstance(raw, dict):
        entries: list[dict[str, Any]] = []
        for date_str, data in raw.items():
            if isinstance(data, dict):
                if "date" not in data:
                    data = {**data, "date": date_str}
                entries.append(data)
        return entries
    return []


def _build_result(
    summary_weeks: list[dict[str, Any]],
    activities: list[dict[str, Any]],
    wellness_data: list[dict[str, Any]],
    start_date: str,
    end_date: str,
    today: datetime,
) -> dict[str, Any]:
    """Build the complete training summary response."""
    if not summary_weeks:
        return {"period": {"start": start_date, "end": end_date}}

    oldest = summary_weeks[0]
    newest = summary_weeks[-1]
    current_ctl = _round1(newest.get("fitness"))
    current_atl = _round1(newest.get("fatigue"))

    load: dict[str, Any] = {
        "start": strip_nulls(
            {
                "ctl": _round1(oldest.get("fitness")),
                "atl": _round1(oldest.get("fatigue")),
                "tsb": _round1(oldest.get("form")),
            }
        ),
        "current": strip_nulls(
            {
                "ctl": current_ctl,
                "atl": current_atl,
                "tsb": _round1(newest.get("form")),
            }
        ),
    }
    if current_atl is not None and current_ctl is not None and current_ctl != 0:
        load["ac_ratio"] = _round2(current_atl / current_ctl)

    return strip_nulls(
        {
            "period": {"start": start_date, "end": end_date},
            "load": strip_nulls(load),
            "period_totals": _build_period_totals(summary_weeks),
            "weeks": _build_weeks(summary_weeks, activities, wellness_data, today),
        }
    )


@mcp.tool()
async def get_training_summary(
    start_date: str | None = None,
    end_date: str | None = None,
    athlete_id: str | None = None,
) -> str:
    """Return a compact JSON training snapshot for the given date range."""
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    start_date, end_date = resolve_date_params(start_date, end_date)

    try:
        validate_date(start_date)
        validate_date(end_date)
    except ValueError as exc:
        return f"Error: {exc}"

    summary_coro = make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/athlete-summary",
        params={"start": start_date, "end": end_date},
    )
    activities_coro = make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/activities",
        params={"oldest": start_date, "newest": end_date},
    )
    wellness_coro = make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/wellness",
        params={"oldest": start_date, "newest": end_date},
    )

    summary_raw, activities_raw, wellness_raw = await asyncio.gather(
        summary_coro, activities_coro, wellness_coro
    )

    for label, raw in [
        ("athlete-summary", summary_raw),
        ("activities", activities_raw),
        ("wellness", wellness_raw),
    ]:
        if isinstance(raw, dict) and "error" in raw:
            return f"Error fetching {label}: {raw.get('message', 'Unknown error')}"

    summary_weeks = summary_raw if isinstance(summary_raw, list) else []
    activities_list = activities_raw if isinstance(activities_raw, list) else []
    wellness_list = _normalise_wellness(wellness_raw)

    summary_weeks.reverse()
    result = _build_result(
        summary_weeks,
        [entry for entry in activities_list if isinstance(entry, dict)],
        wellness_list,
        start_date,
        end_date,
        datetime.now(),
    )
    return json.dumps(result, separators=(",", ":"))
