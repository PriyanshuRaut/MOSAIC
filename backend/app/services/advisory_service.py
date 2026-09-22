from __future__ import annotations

from typing import Any


def _p(week: dict[str, Any], target: str) -> float:
    return float(week["probabilities"][target]["probability"])


def build_weekly_advisory(
    week: dict[str, Any],
    crop: str,
    crop_stage: str,
    irrigation_available: bool,
) -> dict[str, Any]:
    onset = _p(week, "onset")
    break_risk = _p(week, "break")
    revival = _p(week, "revival")
    heavy = _p(week, "heavy_rain")

    actions: list[str] = []

    if crop_stage in {"pre-sowing", "sowing"}:
        if onset >= 0.65 and break_risk < 0.35:
            actions.append(
                f"A potentially favourable {crop} sowing window is indicated; "
                "confirm local field moisture before sowing."
            )
        elif onset >= 0.55 and break_risk >= 0.45:
            actions.append(
                "Initial wet conditions may be followed by a dry spell. "
                "Avoid treating the first rain as a guaranteed sustained onset."
            )
        elif onset < 0.40:
            actions.append(
                "Sustained onset probability is currently low. "
                "Avoid committing all rain-dependent sowing at once."
            )

    if break_risk >= 0.50:
        if irrigation_available:
            actions.append(
                "Elevated dry-spell risk. Keep protective irrigation ready and "
                "prioritise moisture conservation."
            )
        else:
            actions.append(
                "Elevated dry-spell risk with no irrigation reported. "
                "Use conservative sowing/input decisions and moisture-conservation measures."
            )

    if crop_stage in {"germination", "vegetative", "flowering"} and revival >= 0.55:
        actions.append(
            "Rainfall revival probability is elevated. Plan rain-dependent field operations "
            "around the expected return of rainfall while monitoring local updates."
        )

    if heavy >= 0.45:
        actions.append(
            "Elevated heavy-rain risk. Check drainage, avoid waterlogging-sensitive field "
            "operations, and avoid applying inputs immediately before expected intense rain."
        )

    if not actions:
        actions.append(
            "No single dominant monsoon hazard is indicated for this lead week. "
            "Continue routine monitoring and use local agricultural guidance."
        )

    dominant = max(
        [
            ("onset", onset),
            ("break", break_risk),
            ("revival", revival),
            ("heavy rain", heavy),
        ],
        key=lambda pair: pair[1],
    )

    return {
        "lead_week": int(week["lead_week"]),
        "risk_summary": (
            f"Highest model probability: {dominant[0]} "
            f"{dominant[1] * 100.0:.1f}%."
        ),
        "actions": actions,
    }


def build_advisory(
    forecast: dict[str, Any],
    crop: str,
    crop_stage: str,
    irrigation_available: bool,
) -> dict[str, Any]:
    weekly = [
        build_weekly_advisory(
            week,
            crop=crop,
            crop_stage=crop_stage,
            irrigation_available=irrigation_available,
        )
        for week in forecast["weeks"]
    ]

    week1 = forecast["weeks"][0]
    onset = _p(week1, "onset")
    break_risk = _p(week1, "break")
    heavy = _p(week1, "heavy_rain")

    if crop_stage in {"pre-sowing", "sowing"} and onset >= 0.65 and break_risk < 0.35:
        overall = (
            f"For {crop}, the near-term model signal suggests a possible sowing window, "
            "subject to actual field moisture and local agricultural guidance."
        )
    elif break_risk >= 0.50:
        overall = (
            f"For {crop}, dry-spell risk is the main near-term concern. "
            "Prioritise water and soil-moisture planning."
        )
    elif heavy >= 0.45:
        overall = (
            f"For {crop}, heavy-rain risk is the main near-term concern. "
            "Prioritise drainage and protect sensitive field operations."
        )
    else:
        overall = (
            f"For {crop}, no single near-term hazard dominates strongly. "
            "Use the weekly probabilities together with local field conditions."
        )

    return {
        "overall_advisory": overall,
        "weekly_advisories": weekly,
    }
