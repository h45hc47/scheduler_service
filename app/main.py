from fastapi import FastAPI, Query
from typing import Optional

from app.scheduler import Scheduler


app = FastAPI()
scheduler = Scheduler()

@app.get("/busy_slots")
def busy_slots(date: str):
    return scheduler.get_busy_slots(date)

@app.get("/free_slots")
def free_slots(date: str):
    return scheduler.get_free_slots(date)

@app.get("/is_available")
def is_available(date: str, start: str, end: str):
    return {"available": scheduler.is_available(date, start, end)}

@app.get("/find_slot")
def find_slot(duration_minutes: int):
    result = scheduler.find_slot_for_duration(duration_minutes)
    if result:
        return {"date": result[0], "start": result[1], "end": result[2]}
    return {"message": "No available slot found"}

@app.post("/update")
def update():
    scheduler.update_data()
    return {"status": "updated"}
