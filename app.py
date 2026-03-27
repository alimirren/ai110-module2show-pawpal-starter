import streamlit as st
from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task, TaskStatus

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner and Pet Setup")
owner_name = st.text_input("Owner name", value="Jordan")
time_available = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=480, value=60
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

st.caption(f"Owner in session vault: {st.session_state.owner.name}")

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
        st.success(f"Added task '{task.name}' for {selected_pet.name}.")

if owner.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.name,
                "pet": task.pet.name,
                "time": f"{task.scheduled_hour:02d}:{task.scheduled_minute:02d}",
                "duration_minutes": task.duration,
                "priority": task.priority.value,
                "frequency": task.frequency.value,
                "task_type": task.task_type,
                "status": task.status.value,
            }
            for task in owner.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily plan using your Scheduler class.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Generate schedule"):
        scheduler = Scheduler(owner)
        plan = scheduler.create_daily_plan()

        st.subheader("Today's Schedule")
        if plan["tasks"]:
            st.table(
                [
                    {
                        "time": f"{task.scheduled_hour:02d}:{task.scheduled_minute:02d}",
                        "task": task.name,
                        "pet": task.pet.name,
                        "duration": task.duration,
                        "priority": task.priority.value,
                    }
                    for task in plan["tasks"]
                ]
            )
            st.write(f"**Total time scheduled:** {plan['total_duration']} minutes")
            st.write(f"**Time remaining:** {plan['remaining_time']} minutes")
            st.info(scheduler.explain_plan(plan))
        else:
            st.warning("No tasks could be scheduled for today.")

with col2:
    if st.button("Analyze Schedule"):
        scheduler = Scheduler(owner)
        due_tasks = owner.get_due_tasks()

        st.subheader("Schedule Analysis")

        if due_tasks:
            # Time-sorted view
            st.write("**Tasks by Time:**")
            time_sorted = scheduler.sort_tasks_by_time(due_tasks)
            st.table(
                [
                    {
                        "time": f"{task.scheduled_hour:02d}:{task.scheduled_minute:02d}",
                        "task": task.name,
                        "pet": task.pet.name,
                    }
                    for task in time_sorted
                ]
            )

            # Conflict detection
            conflicts = scheduler.detect_conflicts(due_tasks)
            if conflicts:
                st.warning(f"⚠️  **{len(conflicts)} scheduling conflict(s) detected!**")
                for task1, task2 in conflicts:
                    conflict_type = scheduler.get_conflict_type(task1, task2)
                    conflict_label = (
                        "Same pet conflict"
                        if conflict_type == "same_pet"
                        else "Different pets conflict"
                    )
                    st.error(
                        f"{conflict_label}: '{task1.name}' ({task1.scheduled_hour:02d}:{task1.scheduled_minute:02d}-"
                        f"{task1.end_time_minutes//60:02d}:{task1.end_time_minutes%60:02d}) "
                        f"overlaps with '{task2.name}' for {task2.pet.name}"
                    )
            else:
                st.success("✓ No scheduling conflicts detected!")

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
                pet_tasks = owner.filter_tasks_by_pet(pet)
                st.write(f"**{pet.name}'s tasks:** {len(pet_tasks)}")
                st.table(
                    [
                        {
                            "task": t.name,
                            "frequency": t.frequency.value,
                            "status": t.status.value,
                        }
                        for t in pet_tasks
                    ]
                )

    with col_filter2:
        st.subheader("Filter by Status")
        pending = owner.filter_tasks_by_status(TaskStatus.PENDING)
        completed = owner.filter_tasks_by_status(TaskStatus.COMPLETED)
        skipped = owner.filter_tasks_by_status(TaskStatus.SKIPPED)

        st.metric("Pending", len(pending))
        st.metric("Completed", len(completed))
        st.metric("Skipped", len(skipped))

    with col_filter3:
        st.subheader("Task Statistics")
        scheduler = Scheduler(owner)

        # Count by frequency
        daily = len([t for t in owner.tasks if t.frequency == Frequency.DAILY])
        weekly = len([t for t in owner.tasks if t.frequency == Frequency.WEEKLY])
        monthly = len([t for t in owner.tasks if t.frequency == Frequency.MONTHLY])

        st.metric("Daily Tasks", daily)
        st.metric("Weekly Tasks", weekly)
        st.metric("Monthly Tasks", monthly)
