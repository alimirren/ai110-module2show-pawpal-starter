from datetime import date, datetime
from typing import List, Optional, Dict
from enum import Enum

"""Core domain model and scheduling logic for the PawPal+ project."""


class Priority(Enum):
    """Represents how urgent or important a pet care task is."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Frequency(Enum):
    """Represents how often a task should be completed."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Pet:
    """Stores basic information about a pet and the tasks assigned to it."""

    def __init__(self, name: str, type: str, age: int):
        """Create a pet with identifying details and an empty task list."""
        self.name = name
        self.type = type
        self.age = age
        self.tasks: List['Task'] = []


class Task:
    """Represents a care activity associated with a specific pet."""

    def __init__(self, name: str, duration: int, priority: Priority, frequency: Frequency, task_type: str, pet: 'Pet', last_completed: Optional[date] = None):
        """Create a task with scheduling details and an optional completion date."""
        self.name = name
        self.duration = duration
        self.priority = priority
        self.frequency = frequency
        self.task_type = task_type
        self.pet = pet
        self.last_completed = last_completed

    def is_due_today(self, today: date = date.today()) -> bool:
        """Return True when the task should be completed on the given date."""
        if self.last_completed is None:
            return True

        days_since_completed = (today - self.last_completed).days

        if self.frequency == Frequency.DAILY:
            return days_since_completed >= 1
        if self.frequency == Frequency.WEEKLY:
            return days_since_completed >= 7
        if self.frequency == Frequency.MONTHLY:
            return days_since_completed >= 30
        return False

    def mark_completed(self, completion_date: date = date.today()) -> None:
        """Record that the task was completed on the given date."""
        self.last_completed = completion_date


class Owner:
    """Represents the pet owner, their pets, and all managed tasks."""

    def __init__(self, name: str, time_available: int, preferences: List[str]):
        """Create an owner with available time, preferences, pets, and tasks."""
        self.name = name
        self.time_available = time_available
        self.preferences = preferences
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list if it is not already present."""
        if pet not in self.pets:
            self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task for one of the owner's pets and sync it to the pet record."""
        if task.pet not in self.pets:
            raise ValueError("Task pet must belong to this owner.")
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def get_due_tasks(self, today: date = date.today()) -> List[Task]:
        """Return all owner tasks that are due on the given date."""
        return [task for task in self.tasks if task.is_due_today(today)]


class Scheduler:
    """Builds a daily pet care plan based on due tasks and owner constraints."""

    def __init__(self, owner: Owner):
        """Create a scheduler for a specific owner."""
        self.owner = owner

    def create_daily_plan(self, plan_date: date = date.today()) -> Dict:
        """Create a daily plan by filtering, sorting, and fitting due tasks."""
        due_tasks = self.owner.get_due_tasks(plan_date)
        filtered_tasks = self._filter_tasks_by_preferences(due_tasks)
        sorted_tasks = self._sort_tasks(filtered_tasks)
        selected_tasks = self._select_tasks_within_time_limit(sorted_tasks)
        total_duration = sum(task.duration for task in selected_tasks)

        return {
            "date": plan_date,
            "tasks": selected_tasks,
            "total_duration": total_duration,
            "time_available": self.owner.time_available,
            "remaining_time": self.owner.time_available - total_duration,
        }

    def explain_plan(self, plan: Dict) -> str:
        """Return a human-readable explanation of the generated plan."""
        tasks = plan.get("tasks", [])
        if not tasks:
            return "No tasks were scheduled for this day."

        task_summaries = [
            f"{task.name} for {task.pet.name} ({task.priority.value}, {task.duration} min)"
            for task in tasks
        ]
        return (
            f"Scheduled {len(tasks)} task(s) on {plan['date']}: "
            + ", ".join(task_summaries)
            + f". Total time: {plan['total_duration']} minutes."
        )

    def _filter_tasks_by_preferences(self, tasks: List[Task]) -> List[Task]:
        """Prefer tasks whose type matches the owner's stated preferences."""
        if not self.owner.preferences:
            return tasks

        preferred_types = {preference.lower() for preference in self.owner.preferences}
        preferred_tasks = [
            task for task in tasks if task.task_type.lower() in preferred_types
        ]
        return preferred_tasks if preferred_tasks else tasks

    def _sort_tasks(self, tasks: List[Task]) -> List[Task]:
        """Order tasks by priority first, then by shorter duration."""
        priority_order = {
            Priority.HIGH: 0,
            Priority.MEDIUM: 1,
            Priority.LOW: 2,
        }
        return sorted(tasks, key=lambda task: (priority_order[task.priority], task.duration))

    def _select_tasks_within_time_limit(self, tasks: List[Task]) -> List[Task]:
        """Choose tasks in sorted order until the owner's time limit is reached."""
        selected_tasks: List[Task] = []
        total_duration = 0

        for task in tasks:
            if total_duration + task.duration <= self.owner.time_available:
                selected_tasks.append(task)
                total_duration += task.duration

        return selected_tasks
