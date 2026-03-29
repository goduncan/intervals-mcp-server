"""
Sample data for testing Intervals.icu MCP server functions.

This module contains test data structures used across the test suite.
"""

INTERVALS_DATA = {
    "id": "i1",
    "analyzed": True,
    "icu_intervals": [
        {
            "type": "work",
            "label": "Rep 1",
            "elapsed_time": 60,
            "moving_time": 60,
            "distance": 100,
            "average_watts": 200,
            "max_watts": 300,
            "average_watts_kg": 3.0,
            "max_watts_kg": 5.0,
            "weighted_average_watts": 220,
            "intensity": 0.8,
            "training_load": 10,
            "average_heartrate": 150,
            "max_heartrate": 160,
            "average_cadence": 90,
            "max_cadence": 100,
            "average_speed": 6,
            "max_speed": 8,
        }
    ],
}

POWER_CURVES_DATA = {
    "list": [
        {
            "id": "s0",
            "label": "This season",
            "start_date_local": "2025-09-29T00:00:00",
            "end_date_local": "2026-03-14T00:00:00",
            "secs": [5, 15, 60, 3600],
            "values": [780, 620, 380, 210],
            "activity_id": ["i100", "i101", "i102", "i107"],
            "watts_per_kg": [10.4, 8.27, 5.07, 2.8],
        },
        {
            "id": "s1",
            "label": "Last season",
            "start_date_local": "2024-09-29T00:00:00",
            "end_date_local": "2025-03-14T00:00:00",
            "secs": [5, 60, 3600],
            "values": [760, 360, 205],
            "activity_id": ["i200", "i201", "i202"],
            "watts_per_kg": [10.1, 4.8, 2.73],
        },
    ]
}

SPORT_SETTINGS_DATA = [
    {
        "types": ["Ride"],
        "updated": "2026-03-07T21:47:41.692+00:00",
        "ftp": 261,
        "lthr": 170,
        "max_hr": 188,
        "power_zones": [55, 75, 90, 105, 120, 150, 999],
        "power_zone_names": [
            "Active Recovery",
            "Endurance",
            "Tempo",
            "Threshold",
            "VO2 Max",
            "Anaerobic",
            "Neuromuscular",
        ],
        "hr_zones": [120, 140, 155, 170, 188],
        "hr_zone_names": ["Z1", "Z2", "Z3", "Z4", "Z5"],
        "threshold_pace": None,
        "pace_zones": [],
        "pace_zone_names": [],
        "pace_units": None,
    },
    {
        "types": ["Run"],
        "updated": "2026-03-07T21:47:41.692+00:00",
        "ftp": 455,
        "lthr": 181,
        "max_hr": 193,
        "threshold_pace": 3.6363637,
        "pace_units": "MINS_KM",
        "pace_zones": [77.5, 87.5, 95, 102.5, 110, 120, 999],
        "pace_zone_names": ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6", "Zone 7"],
        "hr_zones": [130, 150, 165, 181, 193],
        "hr_zone_names": ["Z1", "Z2", "Z3", "Z4", "Z5"],
    },
]
