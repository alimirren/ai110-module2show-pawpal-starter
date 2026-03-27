from datetime import date

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus


def test_task_completion_updates_last_completed_date() -> None:
    pet = Pet(name="Mochi", type="Dog", age=4)
    task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )
    completion_day = date(2026, 3, 27)

    task.mark_completed(completion_day)

    assert task.last_completed == completion_day


def test_adding_task_increases_pet_task_count() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Luna", type="Cat", age=2)
    owner.add_pet(pet)

    task = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
    )

    starting_task_count = len(pet.tasks)

    owner.add_task(task)

    assert len(pet.tasks) == starting_task_count + 1
    assert pet.tasks[0] == task


def test_task_status_updated_on_completion() -> None:
    pet = Pet(name="Mochi", type="Dog", age=4)
    task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )

    assert task.status == TaskStatus.PENDING
    task.mark_completed()
    assert task.status == TaskStatus.COMPLETED


def test_task_skip_updates_status() -> None:
    pet = Pet(name="Luna", type="Cat", age=2)
    task = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
    )

    assert task.status == TaskStatus.PENDING
    task.skip_task()
    assert task.status == TaskStatus.SKIPPED


def test_filter_tasks_by_pet() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    mochi = Pet(name="Mochi", type="Dog", age=4)
    luna = Pet(name="Luna", type="Cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi_walk = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
    )
    luna_feed = Task(
        name="Feed breakfast",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=luna,
    )

    owner.add_task(mochi_walk)
    owner.add_task(luna_feed)

    mochi_tasks = owner.filter_tasks_by_pet(mochi)
    luna_tasks = owner.filter_tasks_by_pet(luna)

    assert len(mochi_tasks) == 1
    assert len(luna_tasks) == 1
    assert mochi_walk in mochi_tasks
    assert luna_feed in luna_tasks


def test_filter_tasks_by_status() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    task1 = Task(
        name="Task 1",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )
    task2 = Task(
        name="Task 2",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
    )

    owner.add_task(task1)
    owner.add_task(task2)

    task1.mark_completed()

    pending = owner.filter_tasks_by_status(TaskStatus.PENDING)
    completed = owner.filter_tasks_by_status(TaskStatus.COMPLETED)

    assert len(pending) == 1
    assert len(completed) == 1
    assert task2 in pending
    assert task1 in completed


def test_sort_tasks_by_time() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    task1 = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=7,
    )
    task2 = Task(
        name="Afternoon play",
        duration=20,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=14,
    )
    task3 = Task(
        name="Evening walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=18,
    )

    owner.add_task(task3)
    owner.add_task(task1)
    owner.add_task(task2)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_tasks_by_time(owner.tasks)

    assert sorted_tasks[0] == task1  # 7:00
    assert sorted_tasks[1] == task2  # 14:00
    assert sorted_tasks[2] == task3  # 18:00


def test_sort_tasks_by_priority() -> None:
    owner = Owner(name="Jordan", time_available=120, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    high_priority = Task(
        name="Feed",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
    )
    low_priority = Task(
        name="Play",
        duration=30,
        priority=Priority.LOW,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )
    medium_priority = Task(
        name="Groom",
        duration=20,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="grooming",
        pet=pet,
    )

    owner.add_task(low_priority)
    owner.add_task(high_priority)
    owner.add_task(medium_priority)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_tasks_by_priority(owner.tasks)

    assert sorted_tasks[0] == high_priority
    assert sorted_tasks[1] == medium_priority
    assert sorted_tasks[2] == low_priority


def test_detect_time_conflicts() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    task1 = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=7,
        scheduled_minute=0,
    )
    task2 = Task(
        name="Play time",
        duration=25,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=7,
        scheduled_minute=15,  # Overlaps with task1
    )
    task3 = Task(
        name="Feed",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
        scheduled_hour=8,
        scheduled_minute=0,  # No overlap
    )

    owner.add_task(task1)
    owner.add_task(task2)
    owner.add_task(task3)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.tasks)

    assert len(conflicts) == 1
    assert (task1, task2) in conflicts or (task2, task1) in conflicts
    assert scheduler.get_conflict_type(task1, task2) == "same_pet"


def test_detect_time_conflicts_for_different_pets() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    mochi = Pet(name="Mochi", type="Dog", age=4)
    luna = Pet(name="Luna", type="Cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    task1 = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=mochi,
        scheduled_hour=7,
        scheduled_minute=0,
    )
    task2 = Task(
        name="Feed breakfast",
        duration=15,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=luna,
        scheduled_hour=7,
        scheduled_minute=10,
    )

    owner.add_task(task1)
    owner.add_task(task2)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.tasks)

    assert len(conflicts) == 1
    assert (task1, task2) in conflicts or (task2, task1) in conflicts
    assert scheduler.get_conflict_type(task1, task2) == "different_pets"


def test_no_conflicts_non_overlapping_tasks() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    task1 = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=7,
        scheduled_minute=0,
    )
    task2 = Task(
        name="Afternoon play",
        duration=30,
        priority=Priority.MEDIUM,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=14,
        scheduled_minute=0,
    )

    owner.add_task(task1)
    owner.add_task(task2)

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(owner.tasks)

    assert len(conflicts) == 0


def test_mark_tasks_completed_bulk() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])
    pet = Pet(name="Mochi", type="Dog", age=4)
    owner.add_pet(pet)

    task1 = Task(
        name="Task 1",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
    )
    task2 = Task(
        name="Task 2",
        duration=10,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="feeding",
        pet=pet,
    )

    owner.add_task(task1)
    owner.add_task(task2)

    owner.mark_tasks_completed([task1, task2])

    assert task1.status == TaskStatus.COMPLETED
    assert task2.status == TaskStatus.COMPLETED


def test_task_time_properties() -> None:
    pet = Pet(name="Mochi", type="Dog", age=4)
    task = Task(
        name="Morning walk",
        duration=30,
        priority=Priority.HIGH,
        frequency=Frequency.DAILY,
        task_type="exercise",
        pet=pet,
        scheduled_hour=7,
        scheduled_minute=15,
    )

    assert task.start_time_minutes == 435  # 7 * 60 + 15
    assert task.end_time_minutes == 465  # 435 + 30
