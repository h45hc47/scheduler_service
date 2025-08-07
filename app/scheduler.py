import os
import requests
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict

from app.models import ScheduleData


class Scheduler:
    def __init__(self, url: Optional[str] = None):
        self.url = url or os.getenv("SCHEDULE_URL", "https://ofc-test-01.tspb.su/test-task/")
        self.days: Dict[int, dict] = {}
        self.date_to_day_id: Dict[str, int] = {}
        self.timeslots: List[dict] = []
        self.load_data()

    def load_data(self):
        response = requests.get(self.url)
        response.raise_for_status()
        data = ScheduleData(**response.json())
        self.days = {day.id: day.model_dump() for day in data.days}
        self.date_to_day_id = {day.date: day.id for day in data.days}
        self.timeslots = [slot.model_dump() for slot in data.timeslots]

    def update_data(self):
        self.load_data()

    def get_busy_slots(self, date: str) -> List[Tuple[str, str]]:
        day_id = self.date_to_day_id.get(date)
        if day_id is None:
            return []
        slots = [(slot["start"], slot["end"]) for slot in self.timeslots if slot["day_id"] == day_id]
        return sorted(slots)

    def get_free_slots(self, date: str) -> List[Tuple[str, str]]:
        day_id = self.date_to_day_id.get(date)
        if day_id is None:
            return []

        day = self.days[day_id]
        day_start = self._to_dt(date, day["start"])
        day_end = self._to_dt(date, day["end"])

        busy_slots = sorted([
            (self._to_dt(date, slot["start"]), self._to_dt(date, slot["end"]))
            for slot in self.timeslots if slot["day_id"] == day_id
        ])

        free_slots = []
        current = day_start
        for start, end in busy_slots:
            if current < start:
                free_slots.append((self._to_str(current), self._to_str(start)))
            current = max(current, end)

        if current < day_end:
            free_slots.append((self._to_str(current), self._to_str(day_end)))

        return free_slots

    def is_available(self, date: str, start: str, end: str) -> bool:
        day_id = self.date_to_day_id.get(date)
        if day_id is None:
            return False

        day = self.days[day_id]
        day_start = self._to_dt(date, day["start"])
        day_end = self._to_dt(date, day["end"])

        req_start = self._to_dt(date, start)
        req_end = self._to_dt(date, end)

        if not (day_start <= req_start < req_end <= day_end):
            return False

        busy_slots = [
            (self._to_dt(date, slot["start"]), self._to_dt(date, slot["end"]))
            for slot in self.timeslots if slot["day_id"] == day_id
        ]

        for b_start, b_end in busy_slots:
            if not (req_end <= b_start or req_start >= b_end):
                return False
        return True

    def find_slot_for_duration(self, duration_minutes: int) -> Optional[Tuple[str, str, str]]:
        for date, day_id in sorted(self.date_to_day_id.items()):
            free_slots = self.get_free_slots(date)
            for start_str, end_str in free_slots:
                start = self._to_dt(date, start_str)
                end = self._to_dt(date, end_str)
                if (end - start).total_seconds() >= duration_minutes * 60:
                    actual_end = start + timedelta(minutes=duration_minutes)
                    return (date, self._to_str(start), self._to_str(actual_end))
        return None


    def _to_dt(self, date_str: str, time_str: str) -> datetime:
        return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

    def _to_str(self, dt: datetime) -> str:
        return dt.strftime("%H:%M")
