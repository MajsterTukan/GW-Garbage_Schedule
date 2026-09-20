"""Discovery and validation of bundled waste schedules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
from typing import Any

from .const import DATA_DIRECTORY


class ScheduleError(ValueError):
    """Raised when a schedule file is invalid."""


@dataclass(frozen=True, slots=True)
class Schedule:
    """A validated bundled schedule."""

    schedule_id: str
    path: Path
    year: int
    location: str
    source: str
    collection_day: str | None
    dates: dict[str, tuple[date, ...]]


def _load_schedule(path: Path) -> Schedule:
    try:
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise ScheduleError(f"Nie można odczytać {path.name}: {err}") from err

    try:
        year = int(raw["rok"])
        location = str(raw["miejscowosc"]).strip()
        raw_dates = raw["daty"]
    except (KeyError, TypeError, ValueError) as err:
        raise ScheduleError(f"{path.name}: brak poprawnych pól rok, miejscowosc lub daty") from err

    if not location or not isinstance(raw_dates, dict):
        raise ScheduleError(f"{path.name}: miejscowosc lub daty mają niepoprawny format")

    parsed: dict[str, tuple[date, ...]] = {}
    for fraction, values in raw_dates.items():
        if not isinstance(fraction, str) or not isinstance(values, list):
            raise ScheduleError(f"{path.name}: niepoprawny wpis w polu daty")
        try:
            fraction_dates = tuple(sorted({date.fromisoformat(str(value)) for value in values}))
        except ValueError as err:
            raise ScheduleError(f"{path.name}: niepoprawna data w frakcji {fraction}") from err
        if any(value.year != year for value in fraction_dates):
            raise ScheduleError(f"{path.name}: data spoza roku {year}")
        parsed[fraction] = fraction_dates

    if not parsed:
        raise ScheduleError(f"{path.name}: harmonogram nie zawiera frakcji")

    return Schedule(
        schedule_id=path.stem,
        path=path,
        year=year,
        location=location,
        source=str(raw.get("zrodlo", path.name)),
        collection_day=str(raw["dzien_tygodnia"]) if raw.get("dzien_tygodnia") else None,
        dates=parsed,
    )


def discover_schedules(data_directory: Path = DATA_DIRECTORY) -> tuple[dict[str, Schedule], list[str]]:
    """Return valid schedules and messages for ignored invalid files."""
    schedules: dict[str, Schedule] = {}
    errors: list[str] = []
    for path in sorted(data_directory.glob("*.json")):
        try:
            schedule = _load_schedule(path)
        except ScheduleError as err:
            errors.append(str(err))
            continue
        schedules[schedule.schedule_id] = schedule
    return schedules, errors


def schedules_for_year(schedules: dict[str, Schedule], year: int) -> dict[str, Schedule]:
    """Filter schedules by year."""
    return {key: item for key, item in schedules.items() if item.year == year}
