from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus


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
            scheduled_hour=7,
            scheduled_minute=0,
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
            scheduled_hour=8,
            scheduled_minute=0,
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
            scheduled_hour=10,
            scheduled_minute=0,
        )
    )
    owner.add_task(
        Task(
            name="Play with Mochi",
            duration=25,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY,
            task_type="exercise",
            pet=mochi,
            scheduled_hour=7,  # Overlaps with morning walk - creates conflict
            scheduled_minute=15,
        )
    )

    scheduler = Scheduler(owner)
    plan = scheduler.create_daily_plan()

    print("=" * 60)
    print("Today's Schedule")
    print("=" * 60)

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

    print("\n" + "=" * 60)
    print("Task Sorting by Time")
    print("=" * 60)
    due_tasks = owner.get_due_tasks()
    time_sorted = scheduler.sort_tasks_by_time(due_tasks)
    for task in time_sorted:
        time_str = f"{task.scheduled_hour:02d}:{task.scheduled_minute:02d}"
        print(f"  {time_str} - {task.name} ({task.duration} min)")

    print("\n" + "=" * 60)
    print("Tasks Filtered by Pet")
    print("=" * 60)
    mochi_tasks = owner.filter_tasks_by_pet(mochi)
    print(f"Mochi's tasks ({len(mochi_tasks)}):")
    for task in mochi_tasks:
        print(f"  - {task.name} ({task.frequency.value})")

    luna_tasks = owner.filter_tasks_by_pet(luna)
    print(f"\nLuna's tasks ({len(luna_tasks)}):")
    for task in luna_tasks:
        print(f"  - {task.name} ({task.frequency.value})")

    print("\n" + "=" * 60)
    print("Task Status Tracking")
    print("=" * 60)
    print(f"Pending tasks: {len(owner.filter_tasks_by_status(TaskStatus.PENDING))}")
    print(f"Completed tasks: {len(owner.filter_tasks_by_status(TaskStatus.COMPLETED))}")
    print(f"Skipped tasks: {len(owner.filter_tasks_by_status(TaskStatus.SKIPPED))}")

    # Mark some tasks as completed
    owner.mark_tasks_completed(plan["tasks"][:1])
    print("\nAfter marking 1 task complete:")
    print(f"Pending tasks: {len(owner.filter_tasks_by_status(TaskStatus.PENDING))}")
    print(f"Completed tasks: {len(owner.filter_tasks_by_status(TaskStatus.COMPLETED))}")

    print("\n" + "=" * 60)
    print("Conflict Detection")
    print("=" * 60)
    conflicts = scheduler.detect_conflicts(due_tasks)
    if conflicts:
        print(f"⚠️  Found {len(conflicts)} conflict(s):")
        for task1, task2 in conflicts:
            conflict_type = scheduler.get_conflict_type(task1, task2)
            conflict_label = (
                "same pet conflict"
                if conflict_type == "same_pet"
                else "different pets conflict"
            )
            print(
                f"  - {conflict_label}: {task1.name} ({task1.scheduled_hour:02d}:{task1.scheduled_minute:02d}-"
                f"{task1.end_time_minutes//60:02d}:{task1.end_time_minutes%60:02d}) "
                f"overlaps with {task2.name} for {task2.pet.name}"
            )
    else:
        print("✓ No scheduling conflicts detected!")

    print("\n" + "=" * 60)
    print("Recurring Tasks Summary")
    print("=" * 60)
    for frequency in [Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY]:
        tasks_with_freq = [t for t in owner.tasks if t.frequency == frequency]
        print(f"{frequency.value.capitalize()}: {len(tasks_with_freq)} task(s)")


if __name__ == "__main__":
    print_schedule()
