"""JSON storage for shift schedule data."""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Shift(BaseModel):
    """A work shift."""
    id: str
    worker_id: str
    date: date
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    department: str | None = None
    notes: str | None = None


class DayOff(BaseModel):
    """A day off."""
    id: str
    worker_id: str
    date: date
    reason: str | None = None


class RotationPattern(BaseModel):
    """A rotation pattern for scheduling."""
    id: str
    name: str
    worker_ids: list[str]
    cycle_days: int
    pattern: list[str]  # e.g., ["work", "work", "off", "off", "work"]
    start_date: date


class Storage:
    """Handles reading/writing shift schedule data to JSON files."""

    def __init__(self, data_dir: str | Path | None = None):
        if data_dir is None:
            data_dir = Path.home() / ".shift-schedule-mcp"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.shifts_file = self.data_dir / "shifts.json"
        self.days_off_file = self.data_dir / "days_off.json"
        self.rotations_file = self.data_dir / "rotations.json"

        self._init_files()

    def _init_files(self) -> None:
        """Initialize JSON files if they don't exist."""
        for file_path in [self.shifts_file, self.days_off_file, self.rotations_file]:
            if not file_path.exists():
                file_path.write_text("[]")

    def _read_json(self, file_path: Path) -> list[dict[str, Any]]:
        """Read JSON file and return list of dicts."""
        content = file_path.read_text()
        if not content.strip():
            return []
        return json.loads(content)

    def _write_json(self, file_path: Path, data: list[dict[str, Any]]) -> None:
        """Write list of dicts to JSON file."""
        file_path.write_text(json.dumps(data, indent=2, default=str))

    # --- Shifts ---
    def get_shifts(self) -> list[Shift]:
        """Get all shifts."""
        data = self._read_json(self.shifts_file)
        return [Shift(**item) for item in data]

    def get_shift(self, shift_id: str) -> Shift | None:
        """Get a shift by ID."""
        shifts = self.get_shifts()
        for shift in shifts:
            if shift.id == shift_id:
                return shift
        return None

    def get_shifts_by_worker(self, worker_id: str) -> list[Shift]:
        """Get all shifts for a worker."""
        shifts = self.get_shifts()
        return [s for s in shifts if s.worker_id == worker_id]

    def get_shifts_by_date(self, target_date: date) -> list[Shift]:
        """Get all shifts on a specific date."""
        shifts = self.get_shifts()
        return [s for s in shifts if s.date == target_date]

    def get_shifts_by_worker_and_date(self, worker_id: str, target_date: date) -> list[Shift]:
        """Get shifts for a worker on a specific date."""
        shifts = self.get_shifts()
        return [s for s in shifts if s.worker_id == worker_id and s.date == target_date]

    def add_shift(self, shift: Shift) -> Shift:
        """Add a new shift."""
        shifts = self.get_shifts()
        shifts.append(shift)
        self._write_json(self.shifts_file, [s.model_dump() for s in shifts])
        return shift

    def update_shift(self, shift_id: str, **kwargs) -> Shift | None:
        """Update an existing shift."""
        shifts = self.get_shifts()
        for i, shift in enumerate(shifts):
            if shift.id == shift_id:
                updated = shift.model_copy(update=kwargs)
                shifts[i] = updated
                self._write_json(self.shifts_file, [s.model_dump() for s in shifts])
                return updated
        return None

    def delete_shift(self, shift_id: str) -> bool:
        """Delete a shift by ID."""
        shifts = self.get_shifts()
        original_len = len(shifts)
        shifts = [s for s in shifts if s.id != shift_id]
        if len(shifts) < original_len:
            self._write_json(self.shifts_file, [s.model_dump() for s in shifts])
            return True
        return False

    # --- Days Off ---
    def get_days_off(self) -> list[DayOff]:
        """Get all days off."""
        data = self._read_json(self.days_off_file)
        return [DayOff(**item) for item in data]

    def get_day_off(self, day_off_id: str) -> DayOff | None:
        """Get a day off by ID."""
        days = self.get_days_off()
        for day in days:
            if day.id == day_off_id:
                return day
        return None

    def get_days_off_by_worker(self, worker_id: str) -> list[DayOff]:
        """Get all days off for a worker."""
        days = self.get_days_off()
        return [d for d in days if d.worker_id == worker_id]

    def get_days_off_by_date(self, target_date: date) -> list[DayOff]:
        """Get all days off on a specific date."""
        days = self.get_days_off()
        return [d for d in days if d.date == target_date]

    def add_day_off(self, day_off: DayOff) -> DayOff:
        """Add a new day off."""
        days = self.get_days_off()
        days.append(day_off)
        self._write_json(self.days_off_file, [d.model_dump() for d in days])
        return day_off

    def update_day_off(self, day_off_id: str, **kwargs) -> DayOff | None:
        """Update an existing day off."""
        days = self.get_days_off()
        for i, day in enumerate(days):
            if day.id == day_off_id:
                updated = day.model_copy(update=kwargs)
                days[i] = updated
                self._write_json(self.days_off_file, [d.model_dump() for d in days])
                return updated
        return None

    def delete_day_off(self, day_off_id: str) -> bool:
        """Delete a day off by ID."""
        days = self.get_days_off()
        original_len = len(days)
        days = [d for d in days if d.id != day_off_id]
        if len(days) < original_len:
            self._write_json(self.days_off_file, [d.model_dump() for d in days])
            return True
        return False

    # --- Rotation Patterns ---
    def get_rotations(self) -> list[RotationPattern]:
        """Get all rotation patterns."""
        data = self._read_json(self.rotations_file)
        return [RotationPattern(**item) for item in data]

    def get_rotation(self, rotation_id: str) -> RotationPattern | None:
        """Get a rotation pattern by ID."""
        rotations = self.get_rotations()
        for rot in rotations:
            if rot.id == rotation_id:
                return rot
        return None

    def get_rotations_by_worker(self, worker_id: str) -> list[RotationPattern]:
        """Get all rotation patterns that include a worker."""
        rotations = self.get_rotations()
        return [r for r in rotations if worker_id in r.worker_ids]

    def add_rotation(self, rotation: RotationPattern) -> RotationPattern:
        """Add a new rotation pattern."""
        rotations = self.get_rotations()
        rotations.append(rotation)
        self._write_json(self.rotations_file, [r.model_dump() for r in rotations])
        return rotation

    def update_rotation(self, rotation_id: str, **kwargs) -> RotationPattern | None:
        """Update an existing rotation pattern."""
        rotations = self.get_rotations()
        for i, rot in enumerate(rotations):
            if rot.id == rotation_id:
                updated = rot.model_copy(update=kwargs)
                rotations[i] = updated
                self._write_json(self.rotations_file, [r.model_dump() for r in rotations])
                return updated
        return None

    def delete_rotation(self, rotation_id: str) -> bool:
        """Delete a rotation pattern by ID."""
        rotations = self.get_rotations()
        original_len = len(rotations)
        rotations = [r for r in rotations if r.id != rotation_id]
        if len(rotations) < original_len:
            self._write_json(self.rotations_file, [r.model_dump() for r in rotations])
            return True
        return False


def create_storage() -> Storage:
    """Factory function to create storage with default path."""
    return Storage()