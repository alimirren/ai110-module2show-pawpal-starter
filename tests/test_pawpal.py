from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus


def make_owner_with_pets() -> tuple[Owner, Pet, Pet]:
    owner = Owner(name="Jordan", time_available=50, preferences=[])
    mochi = Pet(name="Mochi", type="Dog", age=4)
    luna = Pet(name="Luna", type="Cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner, mochi, luna


def test_owner_get_due_tasks_only_returns_tasks_due_for_today() -> None:
    owner, mochi, _ = make_owner_with_pets()
    today = date(2026, 3, 27)

    daily_due = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        last_completed=today.replace(day=26),
    )
    daily_not_due = Task(
        name="Evening walk",
        duration=20,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        last_completed=today,
    )
    weekly_due = Task(
        name="Brush coat",
        duration=15,
        priority=Priority.LOW,
        frequency=Frequency.WEEKLY,
        task_type="grooming",
        pet=mochi,
        last_completed=date(2026, 3, 19),
    )
    monthly_not_due = Task(
        name="Flea treatment",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.MONTHLY,
        task_type="health",
        pet=mochi,
        last_completed=date(2026, 3, 10),
    )

    for task in [daily_due, daily_not_due, weekly_due, monthly_not_due]:
        owner.add_task(task)

    due_tasks = owner.get_due_tasks(today)

    assert due_tasks == [daily_due, weekly_due]


def test_create_daily_plan_orders_by_priority_and_respects_time_available() -> None:
    owner, mochi, luna = make_owner_with_pets()

    high_short = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=luna,
    )
    high_long = Task(
        name="Morning walk",
        duration=25,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
    )
    medium_fits = Task(
        name="Brush coat",
        duration=15,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="grooming",
        pet=mochi,
    )
    low_skipped_for_time = Task(
        name="Play time",
        duration=20,
        priority=Priority.LOW,
        frequency=Frequency.DAILY,
        task_type="enrichment",
        pet=luna,
    )

    for task in [medium_fits, low_skipped_for_time, high_long, high_short]:
        owner.add_task(task)

    plan = Scheduler(owner).create_daily_plan(date(2026, 3, 27))

    assert plan["tasks"] == [high_short, high_long, medium_fits]
    assert plan["total_duration"] == 50
    assert plan["remaining_time"] == 0
    assert sum(task.duration for task in plan["tasks"]) <= owner.time_available


def test_sort_tasks_by_time_returns_tasks_in_chronological_order() -> None:
    owner, mochi, _ = make_owner_with_pets()
    earliest = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=mochi,
        scheduled_hour=7,
        scheduled_minute=15,
    )
    middle = Task(
        name="Morning walk",
        duration=25,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        scheduled_hour=9,
        scheduled_minute=0,
    )
    latest = Task(
        name="Evening play",
        duration=20,
        priority=Priority.LOW,
        frequency=Frequency.DAILY,
        task_type="enrichment",
        pet=mochi,
        scheduled_hour=18,
        scheduled_minute=30,
    )

    sorted_tasks = Scheduler(owner).sort_tasks_by_time([latest, middle, earliest])

    assert sorted_tasks == [earliest, middle, latest]


def test_task_status_updates_for_completion_and_skip() -> None:
    pet = Pet(name="Mochi", type="Dog", age=4)
    completed_task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )
    skipped_task = Task(
        name="Brush coat",
        duration=15,
        priority=Priority.MEDIUM,
        frequency=Frequency.WEEKLY,
        task_type="grooming",
        pet=pet,
    )

    completed_task.mark_completed(date(2026, 3, 27), auto_reschedule=False)
    skipped_task.skip_task()

    assert completed_task.status == TaskStatus.COMPLETED
    assert skipped_task.status == TaskStatus.SKIPPED


def test_mark_completed_creates_new_daily_task_for_following_day() -> None:
    owner, mochi, _ = make_owner_with_pets()
    original_task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
    )
    owner.add_task(original_task)
    completion_date = date(2026, 3, 27)

    owner.mark_tasks_completed([original_task], completion_date)

    assert original_task.status == TaskStatus.COMPLETED
    assert original_task.last_completed == completion_date
    assert len(owner.tasks) == 2

    follow_up_task = owner.tasks[1]
    assert follow_up_task is not original_task
    assert follow_up_task.name == original_task.name
    assert follow_up_task.pet is original_task.pet
    assert follow_up_task.frequency == Frequency.DAILY
    assert follow_up_task.status == TaskStatus.PENDING
    assert follow_up_task.last_completed == completion_date


def test_owner_add_task_keeps_owner_and_pet_task_lists_in_sync() -> None:
    owner, mochi, _ = make_owner_with_pets()
    task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
    )

    owner.add_task(task)

    assert task in owner.tasks
    assert task in mochi.tasks
    assert owner.tasks[0] is mochi.tasks[0]


def test_detect_conflicts_finds_overlaps_and_classifies_pet_relationships() -> None:
    owner, mochi, luna = make_owner_with_pets()

    same_pet_first = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        scheduled_hour=7,
        scheduled_minute=0,
    )
    same_pet_second = Task(
        name="Medication",
        duration=15,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="health",
        pet=mochi,
        scheduled_hour=7,
        scheduled_minute=20,
    )
    different_pet_overlap = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=luna,
        scheduled_hour=7,
        scheduled_minute=25,
    )
    no_conflict = Task(
        name="Evening play",
        duration=20,
        priority=Priority.LOW,
        frequency=Frequency.DAILY,
        task_type="enrichment",
        pet=luna,
        scheduled_hour=9,
        scheduled_minute=0,
    )

    for task in [same_pet_first, same_pet_second, different_pet_overlap, no_conflict]:
        owner.add_task(task)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.tasks)

    assert conflicts == [
        (same_pet_first, same_pet_second),
        (same_pet_first, different_pet_overlap),
        (same_pet_second, different_pet_overlap),
    ]
    assert scheduler.get_conflict_type(*conflicts[0]) == "same_pet"
    assert scheduler.get_conflict_type(*conflicts[1]) == "different_pets"


def test_detect_conflicts_flags_tasks_with_duplicate_start_times() -> None:
    owner, mochi, luna = make_owner_with_pets()
    first_task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        scheduled_hour=8,
        scheduled_minute=0,
    )
    duplicate_time_task = Task(
        name="Feed breakfast",
        duration=15,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=luna,
        scheduled_hour=8,
        scheduled_minute=0,
    )

    owner.add_task(first_task)
    owner.add_task(duplicate_time_task)

    conflicts = Scheduler(owner).detect_conflicts(owner.tasks)

    assert conflicts == [(first_task, duplicate_time_task)]
