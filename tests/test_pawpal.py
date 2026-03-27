from datetime import date

from pawpal_system import Frequency, Owner, Pet, Priority, Task


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
