from datetime import date, datetime
from typing import List, Optional, Dict
from enum import Enum


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Pet:
    def __init__(self, name: str, type: str, age: int):
        self.name = name
        self.type = type
        self.age = age


class Task:
    def __init__(self, name: str, duration: int, priority: Priority, frequency: Frequency, task_type: str, pet: 'Pet', last_completed: Optional[date] = None):
        self.name = name
        self.duration = duration
        self.priority = priority
        self.frequency = frequency
        self.task_type = task_type
        self.pet = pet
        self.last_completed = last_completed

    def is_due_today(self, today: date = date.today()) -> bool:
        pass

    def mark_completed(self, completion_date: date = date.today()) -> None:
        pass


class Owner:
    def __init__(self, name: str, time_available: int, preferences: List[str]):
        self.name = name
        self.time_available = time_available
        self.preferences = preferences
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def get_due_tasks(self, today: date = date.today()) -> List[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def create_daily_plan(self, plan_date: date = date.today()) -> Dict:
        pass

    def explain_plan(self, plan: Dict) -> str:
        pass

    def _filter_tasks_by_preferences(self, tasks: List[Task]) -> List[Task]:
        pass

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def _select_tasks_within_time_limit(self, tasks: List[Task]) -> List[Task]:
        pass
