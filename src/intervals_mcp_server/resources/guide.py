"""Usage guide resource for the Intervals.icu MCP server."""

from intervals_mcp_server import mcp_instance

USAGE_GUIDE = """\
INTERVALS.ICU MCP SERVER - USAGE GUIDE

CONCEPTS

Activities - completed sessions uploaded from a device. Historical only.
  Types: Ride, Run, Swim, Walk, Workout, WeightTraining, VirtualRide, etc.
  Key distinction: some types (Workout, WeightTraining) contribute 0% to
  fitness (CTL) but 100% to fatigue (ATL) by design in intervals.icu.

Events - items on the athlete's calendar.
  Planned workouts may later link to completed activities.

Wellness - one entry per day. Athlete-logged or device-synced.
  Not tied to activities. Gaps are common.

Athlete Zones:
  Power zones, heart rate zones, pace zones, and thresholds are sport-specific.
  Query current zones before prescribing targets.

RECOMMENDED WORKFLOWS

Start of any coaching conversation:
  1. get_training_summary(start_date, end_date)
  2. get_athlete_zones(sport)

Analysing a completed activity:
  1. get_activities()
  2. get_activity_details(id)
  3. get_activity_intervals(id)

Planning and calendar management:
  1. get_events()
  2. add_or_update_event()

AVAILABLE TOOLS

  get_training_summary      Weekly load snapshot
  get_athlete_zones         FTP, LTHR, and zone boundaries by sport
  get_athlete_power_curves  Best power by duration across time ranges
  get_activities            Completed session list with load metrics
  get_activity_details      Full metrics for a single activity
  get_activity_intervals    Interval breakdown for a structured activity
  get_wellness_data         Daily wellness entries
  get_events                Calendar events
"""


def coaching_context_protocol() -> str:
    """Return the usage guide resource for the server."""
    return USAGE_GUIDE


if mcp_instance.mcp is not None:
    coaching_context_protocol = mcp_instance.mcp.resource("intervals-icu://guide")(
        coaching_context_protocol
    )
