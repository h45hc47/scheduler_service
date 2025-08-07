from typing import List
from pydantic import BaseModel


class Day(BaseModel):
    id: int
    date: str
    start: str
    end: str

class Timeslot(BaseModel):
    id: int
    day_id: int
    start: str
    end: str

class ScheduleData(BaseModel):
    days: List[Day]
    timeslots: List[Timeslot]
