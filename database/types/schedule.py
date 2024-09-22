from typing import TypedDict
from datetime import datetime

class Schedule(TypedDict):
    group: int
    week_type: str
    day: str
    lessons: dict
    creation_time: datetime
    
class Lessons(TypedDict):
    name: str
    lesson_type: str
    location: str
    tutor: str