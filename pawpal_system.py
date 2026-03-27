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


class TaskStatus(Enum):
    """Represents the current state of a task."""

    PENDING = "pending"
    COMPLETED = "completed"
    SKIPPED = "skipped"


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

    def __init__(self, name: str, duration: int, priority: Priority, frequency: Frequency, task_type: str, pet: 'Pet', last_completed: Optional[date] = None, scheduled_hour: int = 9, scheduled_minute: int = 0, status: 'TaskStatus' = None):
        """Create a task with scheduling details, time, and status tracking."""
        self.name = name
        self.duration = duration
        self.priority = priority
        self.frequency = frequency
        self.task_type = task_type
        self.pet = pet
        self.last_completed = last_completed
        self.scheduled_hour = scheduled_hour
        self.scheduled_minute = scheduled_minute
        self.status = status or TaskStatus.PENDING

    @property
    def end_time_minutes(self) -> int:
        """Return the end time of this task in minutes since midnight."""
        start_minutes = self.scheduled_hour * 60 + self.scheduled_minute
        return start_minutes + self.duration

    @property
    def start_time_minutes(self) -> int:
        """Return the start time of this task in minutes since midnight."""
        return self.scheduled_hour * 60 + self.scheduled_minute

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

    def mark_completed(self, completion_date: date = date.today(), auto_reschedule: bool = True) -> Optional['Task']:
        """Record that the task was completed on the given date and update status.

        If auto_reschedule is True and the task is recurring (daily or weekly),
        create and return a cloned task for the next occurrence.
        """
        self.last_completed = completion_date
        self.status = TaskStatus.COMPLETED

        if auto_reschedule and self.frequency in (Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY):
            new_task = Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                frequency=self.frequency,
                task_type=self.task_type,
                pet=self.pet,
                last_completed=completion_date,
                scheduled_hour=self.scheduled_hour,
                scheduled_minute=self.scheduled_minute,
                status=TaskStatus.PENDING,
            )
            return new_task

        return None

    def skip_task(self) -> None:
        """Mark the task as skipped for today."""
        self.status = TaskStatus.SKIPPED


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

    def filter_tasks_by_pet(self, pet: Pet) -> List[Task]:
        """Return all tasks assigned to a specific pet."""
        return [task for task in self.tasks if task.pet == pet]

    def filter_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Return all tasks with a specific status."""
        return [task for task in self.tasks if task.status == status]

    def mark_tasks_completed(self, tasks: List[Task], completion_date: date = date.today()) -> None:
        """Mark multiple tasks as completed at once, and reschedule recurring tasks."""
        for task in tasks:
            if task in self.tasks:
                new_task = task.mark_completed(completion_date)
                if new_task is not None:
                    self.add_task(new_task)


class Scheduler:
    """Builds a daily pet care plan based on due tasks and owner constraints."""

    # Priority order cached for efficiency
    PRIORITY_ORDER = {
        Priority.HIGH: 0,
        Priority.MEDIUM: 1,
        Priority.LOW: 2,
    }

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

    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by scheduled time."""
        return sorted(tasks, key=lambda task: (task.scheduled_hour, task.scheduled_minute))

    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority first, then by shorter duration."""
        return sorted(tasks, key=lambda task: (self.PRIORITY_ORDER[task.priority], task.duration))

    def detect_conflicts(self, tasks: List[Task]) -> List[tuple]:
        """
        Detect time conflicts between tasks for the same pet.
        Returns a list of conflict tuples: [(task1, task2), ...]
        """
        conflicts = []
        tasks_by_pet = {}

        for task in tasks:
            if task.pet not in tasks_by_pet:
                tasks_by_pet[task.pet] = []
            tasks_by_pet[task.pet].append(task)

        # Check for overlaps within each pet's tasks
        for pet, pet_tasks in tasks_by_pet.items():
            for i, task1 in enumerate(pet_tasks):
                for task2 in pet_tasks[i + 1 :]:
                    # Check if time ranges overlap
                    if self._tasks_overlap(task1, task2):
                        conflicts.append((task1, task2))

        return conflicts

    def _tasks_overlap(self, task1: Task, task2: Task) -> bool:
        """Check if two tasks have overlapping time slots."""
        return (task1.start_time_minutes < task2.end_time_minutes and 
                task2.start_time_minutes < task1.end_time_minutes)

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
        return self.sort_tasks_by_priority(tasks)

    def _select_tasks_within_time_limit(self, tasks: List[Task]) -> List[Task]:
        """Choose tasks in sorted order until the owner's time limit is reached."""
        selected_tasks: List[Task] = []
        total_duration = 0

        for task in tasks:
            if total_duration + task.duration <= self.owner.time_available:
                selected_tasks.append(task)
                total_duration += task.duration
            elif self.owner.time_available - total_duration < task.duration:
                # Early exit: no remaining task will fit
                break

        return selected_tasks
