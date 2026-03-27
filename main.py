from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task


def print_schedule() -> None:
    owner = Owner(name="Jordan", time_available=90, preferences=[])

    mochi = Pet(name="Mochi", type="Dog", age=4)
    luna = Pet(name="Luna", type="Cat", age=2)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    owner.add_task(
        Task(
            name="Morning walk",
            duration=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            task_type="exercise",
            pet=mochi,
        )
    )
    owner.add_task(
        Task(
            name="Feed breakfast",
            duration=10,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
            task_type="feeding",
            pet=luna,
        )
    )
    owner.add_task(
        Task(
            name="Brush fur",
            duration=20,
            priority=Priority.MEDIUM,
            frequency=Frequency.WEEKLY,
            task_type="grooming",
            pet=mochi,
        )
    )

    scheduler = Scheduler(owner)
    plan = scheduler.create_daily_plan()

    print("Today's Schedule")
    print("----------------")

    if not plan["tasks"]:
        print("No tasks scheduled for today.")
        return

    for index, task in enumerate(plan["tasks"], start=1):
        print(
            f"{index}. {task.name} for {task.pet.name} "
            f"({task.duration} min, {task.priority.value} priority)"
        )

    print(f"\nTotal time scheduled: {plan['total_duration']} minutes")
    print(f"Time remaining: {plan['remaining_time']} minutes")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    print_schedule()
