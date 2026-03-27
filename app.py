import json
from datetime import date
from pathlib import Path

import streamlit as st
from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus


STATE_FILE = Path(__file__).resolve().with_name("pawpal_state.json")


def serialize_owner(owner: Owner) -> dict:
    """Convert the owner object graph into JSON-safe data."""
    return {
        "name": owner.name,
        "time_available": owner.time_available,
        "preferences": owner.preferences,
        "pets": [
            {
                "name": pet.name,
                "type": pet.type,
                "age": pet.age,
            }
            for pet in owner.pets
        ],
        "tasks": [
            {
                "name": task.name,
                "duration": task.duration,
                "priority": task.priority.value,
                "frequency": task.frequency.value,
                "task_type": task.task_type,
                "pet_name": task.pet.name,
                "last_completed": (
                    task.last_completed.isoformat() if task.last_completed else None
                ),
                "scheduled_hour": task.scheduled_hour,
                "scheduled_minute": task.scheduled_minute,
                "status": task.status.value,
            }
            for task in owner.tasks
        ],
    }


def load_owner_from_disk() -> Owner | None:
    """Load a previously saved owner and related data from disk."""
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open() as state_file:
        data = json.load(state_file)

    owner = Owner(
        name=data["name"],
        time_available=data["time_available"],
        preferences=data.get("preferences", []),
    )

    pets_by_name: dict[str, Pet] = {}
    for pet_data in data.get("pets", []):
        pet = Pet(
            name=pet_data["name"],
            type=pet_data["type"],
            age=pet_data["age"],
        )
        owner.add_pet(pet)
        pets_by_name[pet.name] = pet

    for task_data in data.get("tasks", []):
        pet = pets_by_name.get(task_data["pet_name"])
        if pet is None:
            continue

        owner.add_task(
            Task(
                name=task_data["name"],
                duration=task_data["duration"],
                priority=Priority(task_data["priority"]),
                frequency=Frequency(task_data["frequency"]),
                task_type=task_data["task_type"],
                pet=pet,
                last_completed=(
                    date.fromisoformat(task_data["last_completed"])
                    if task_data["last_completed"]
                    else None
                ),
                scheduled_hour=task_data.get("scheduled_hour", 9),
                scheduled_minute=task_data.get("scheduled_minute", 0),
                status=TaskStatus(task_data.get("status", TaskStatus.PENDING.value)),
            )
        )

    return owner


def save_owner_to_disk(owner: Owner) -> None:
    """Persist the current owner, pets, and tasks to disk."""
    with STATE_FILE.open("w") as state_file:
        json.dump(serialize_owner(owner), state_file, indent=2)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown(
    """
Welcome to **PawPal+**, your pet care planning assistant.

This app helps you organize pet care tasks, build a daily schedule, spot timing conflicts,
and stay on top of recurring activities like walks, feeding, grooming, and medication.
"""
)

st.divider()

st.subheader("Owner and Pet Setup")
if "owner" not in st.session_state:
    st.session_state.owner = load_owner_from_disk()

saved_owner = st.session_state.owner
default_owner_name = saved_owner.name if isinstance(saved_owner, Owner) else "Jordan"
default_time_available = (
    saved_owner.time_available if isinstance(saved_owner, Owner) else 60
)

owner_name = st.text_input("Owner name", value=default_owner_name)
time_available = st.number_input(
    "Time available today (minutes)",
    min_value=1,
    max_value=480,
    value=default_time_available,
)

# Treat session_state like a small per-user "vault" for persistent objects.
owner_in_vault = st.session_state.get("owner")
if isinstance(owner_in_vault, Owner):
    owner = owner_in_vault
    owner.name = owner_name
    owner.time_available = int(time_available)
else:
    owner = Owner(name=owner_name, time_available=int(time_available), preferences=[])
    st.session_state.owner = owner

save_owner_to_disk(owner)

scheduler = Scheduler(owner)

st.caption(f"Owner in session vault: {st.session_state.owner.name}")


def format_task_time(task: Task) -> str:
    """Return a readable start-end time label for a task."""
    end_hour, end_minute = divmod(task.end_time_minutes, 60)
    return (
        f"{task.scheduled_hour:02d}:{task.scheduled_minute:02d}-"
        f"{end_hour:02d}:{end_minute:02d}"
    )


def task_table_rows(tasks: list[Task]) -> list[dict]:
    """Convert tasks into a consistent table-friendly structure."""
    return [
        {
            "time": format_task_time(task),
            "title": task.name,
            "pet": task.pet.name,
            "duration_minutes": task.duration,
            "priority": task.priority.value,
            "frequency": task.frequency.value,
            "task_type": task.task_type,
            "status": task.status.value,
        }
        for task in tasks
    ]


def render_task_table(tasks: list[Task], empty_message: str) -> None:
    """Show a consistent sorted task table or an empty-state message."""
    if tasks:
        st.table(task_table_rows(tasks))
    else:
        st.info(empty_message)


def task_label(index: int, task: Task) -> str:
    """Return a readable unique label for selecting a task in the UI."""
    return (
        f"{index + 1}. {task.name} for {task.pet.name} "
        f"({format_task_time(task)}, {task.status.value})"
    )


def show_conflict_warnings(tasks: list[Task], warning_message: str, conflicts: list[tuple[Task, Task]] | None = None) -> None:
    """Render scheduler-based conflict warnings for a task list."""
    conflicts = conflicts if conflicts is not None else scheduler.detect_conflicts(tasks)
    if not conflicts:
        st.success("No scheduling conflicts detected.")
        return

    st.warning(warning_message)
    for task1, task2 in conflicts:
        conflict_type = scheduler.get_conflict_type(task1, task2)
        conflict_label = (
            "Same pet conflict" if conflict_type == "same_pet" else "Different pets conflict"
        )
        st.error(
            f"{conflict_label}: '{task1.name}' ({format_task_time(task1)}) overlaps with "
            f"'{task2.name}' for {task2.pet.name} ({format_task_time(task2)})"
        )

pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=50, value=4)

if st.button("Add pet"):
    existing_pet = next(
        (pet for pet in owner.pets if pet.name.lower() == pet_name.lower()),
        None,
    )
    if existing_pet:
        st.info(f"{existing_pet.name} is already in {owner.name}'s pet list.")
    else:
        pet = Pet(name=pet_name, type=species, age=int(pet_age))
        owner.add_pet(pet)
        save_owner_to_disk(owner)
        st.success(f"Added {pet.name} the {pet.type}.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [{"name": pet.name, "species": pet.type, "age": pet.age} for pet in owner.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add tasks using the methods from your PawPal system.")

if owner.pets:
    pet_options = {f"{pet.name} ({pet.type})": pet for pet in owner.pets}
    selected_pet_label = st.selectbox("Assign task to pet", list(pet_options.keys()))
    selected_pet = pet_options[selected_pet_label]
else:
    selected_pet = None
    st.warning("Add a pet before scheduling tasks.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"], index=0)

col_type, col_hour, col_min = st.columns(3)
with col_type:
    task_type = st.text_input("Task type", value="exercise")
with col_hour:
    scheduled_hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=9)
with col_min:
    scheduled_minute = st.number_input("Minute (0-59)", min_value=0, max_value=59, value=0, step=5)

if st.button("Add task"):
    if selected_pet is None:
        st.error("Please add a pet before adding tasks.")
    else:
        priority_map = {
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
        }
        frequency_map = {
            "daily": Frequency.DAILY,
            "weekly": Frequency.WEEKLY,
            "monthly": Frequency.MONTHLY,
        }
        task = Task(
            name=task_title,
            duration=int(duration),
            priority=priority_map[priority],
            frequency=frequency_map[frequency],
            task_type=task_type,
            pet=selected_pet,
            scheduled_hour=int(scheduled_hour),
            scheduled_minute=int(scheduled_minute),
        )
        owner.add_task(task)
        save_owner_to_disk(owner)
        st.success(f"Added task '{task.name}' for {selected_pet.name}.")

if owner.tasks:
    st.write("Current tasks:")
    current_tasks = scheduler.sort_tasks_by_time(owner.tasks)
    current_conflicts = scheduler.detect_conflicts(current_tasks)
    render_task_table(current_tasks, "No tasks yet. Add one above.")
    show_conflict_warnings(
        current_tasks,
        f"Found {len(current_conflicts)} conflict(s) in the current task list.",
        current_conflicts,
    )

    st.markdown("#### Task Actions")
    task_options = {
        task_label(index, task): task for index, task in enumerate(current_tasks)
    }
    selected_task_label = st.selectbox(
        "Select a task to manage",
        list(task_options.keys()),
        key="task_action_select",
    )
    selected_task = task_options[selected_task_label]

    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("Mark completed"):
            owner.mark_task_completed(selected_task)
            save_owner_to_disk(owner)
            st.success(f"Marked '{selected_task.name}' as completed.")
            st.rerun()
    with action_col2:
        if st.button("Skip task"):
            owner.skip_task(selected_task)
            save_owner_to_disk(owner)
            st.warning(f"Skipped '{selected_task.name}'.")
            st.rerun()
    with action_col3:
        if st.button("Remove task"):
            owner.remove_task(selected_task)
            save_owner_to_disk(owner)
            st.success(f"Removed '{selected_task.name}'.")
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily plan using your Scheduler class.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Generate schedule"):
        plan = scheduler.create_daily_plan()
        scheduled_tasks = scheduler.sort_tasks_by_time(plan["tasks"])
        scheduled_conflicts = scheduler.detect_conflicts(scheduled_tasks)

        st.subheader("Today's Schedule")
        if scheduled_tasks:
            st.success(
                f"Scheduled {len(scheduled_tasks)} task(s) within {plan['time_available']} available minutes."
            )
            st.table(
                [
                    {
                        "time": format_task_time(task),
                        "task": task.name,
                        "pet": task.pet.name,
                        "duration": task.duration,
                        "priority": task.priority.value,
                    }
                    for task in scheduled_tasks
                ]
            )
            st.write(f"**Total time scheduled:** {plan['total_duration']} minutes")
            st.write(f"**Time remaining:** {plan['remaining_time']} minutes")
            show_conflict_warnings(
                scheduled_tasks,
                f"Found {len(scheduled_conflicts)} conflict(s) in today's schedule.",
                scheduled_conflicts,
            )
            st.info(scheduler.explain_plan(plan))
        else:
            st.warning("No tasks could be scheduled for today.")

with col2:
    if st.button("Analyze Schedule"):
        due_tasks = owner.get_due_tasks()

        st.subheader("Schedule Analysis")

        if due_tasks:
            # Time-sorted view
            time_sorted = scheduler.sort_tasks_by_time(due_tasks)
            st.success(f"Found {len(time_sorted)} due task(s) ready for today's review.")
            st.write("**Tasks by Time:**")
            st.table(
                [
                    {
                        "time": format_task_time(task),
                        "task": task.name,
                        "pet": task.pet.name,
                        "priority": task.priority.value,
                        "status": task.status.value,
                    }
                    for task in time_sorted
                ]
            )

            # Conflict detection
            conflicts = scheduler.detect_conflicts(time_sorted)
            show_conflict_warnings(
                time_sorted,
                f"Found {len(conflicts)} scheduling conflict(s) in the due-task list.",
                conflicts,
            )
        else:
            st.info("No due tasks to analyze right now.")

st.divider()

if owner.tasks:
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        st.subheader("Filter by Pet")
        pet_names = [f"{pet.name}" for pet in owner.pets]
        selected_pet_filter = st.selectbox(
            "Select a pet", pet_names, key="pet_filter"
        )
        for pet in owner.pets:
            if pet.name == selected_pet_filter:
                pet_tasks = scheduler.sort_tasks_by_time(owner.filter_tasks_by_pet(pet))
                st.success(f"{pet.name} has {len(pet_tasks)} task(s) in the schedule.")
                st.table(
                    [
                        {
                            "time": format_task_time(t),
                            "task": t.name,
                            "frequency": t.frequency.value,
                            "priority": t.priority.value,
                            "status": t.status.value,
                        }
                        for t in pet_tasks
                    ]
                )
                pet_conflicts = scheduler.detect_conflicts(pet_tasks)
                show_conflict_warnings(
                    pet_tasks,
                    f"Found {len(pet_conflicts)} conflict(s) for {pet.name}.",
                    pet_conflicts,
                )

    with col_filter2:
        st.subheader("Filter by Status")
        pending = owner.filter_tasks_by_status(TaskStatus.PENDING)
        completed = owner.filter_tasks_by_status(TaskStatus.COMPLETED)
        skipped = owner.filter_tasks_by_status(TaskStatus.SKIPPED)

        st.metric("Pending", len(pending))
        st.metric("Completed", len(completed))
        st.metric("Skipped", len(skipped))
        if pending:
            st.warning("Pending tasks still need attention.")
            st.table(task_table_rows(scheduler.sort_tasks_by_time(pending)))
        elif completed or skipped:
            st.success("No pending tasks remain in the current list.")

    with col_filter3:
        st.subheader("Task Statistics")
        # Count by frequency
        daily = len([t for t in owner.tasks if t.frequency == Frequency.DAILY])
        weekly = len([t for t in owner.tasks if t.frequency == Frequency.WEEKLY])
        monthly = len([t for t in owner.tasks if t.frequency == Frequency.MONTHLY])

        st.metric("Daily Tasks", daily)
        st.metric("Weekly Tasks", weekly)
        st.metric("Monthly Tasks", monthly)
