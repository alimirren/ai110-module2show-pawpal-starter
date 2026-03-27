# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- Due-task filtering: tasks are included in planning only when they are due based on daily, weekly, or monthly recurrence rules.
- Sorting by priority: the scheduler ranks tasks by priority first and then by shorter duration when building a plan.
- Sorting by time: task lists can be displayed in chronological order using scheduled hour and minute.
- Time-limit selection: daily plans include only the tasks that fit within the owner's available minutes.
- Conflict warnings: overlapping tasks are detected and flagged in the UI.
- Conflict classification: overlaps are labeled as either same-pet conflicts or different-pet conflicts.
- Daily recurrence: completing a recurring task creates a follow-up pending task for the next cycle.
- Task status tracking: tasks can move between pending, completed, and skipped states.
- Plan explanation: the app generates a readable summary of why the daily plan was selected.
- Owner and pet task synchronization: when a task is added to an owner, it is also linked to the correct pet.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

The current test suite covers the most important scheduling and task-management behaviors, including due-task filtering, chronological sorting, priority-based daily planning within the owner's time limit, task status updates, recurring daily task creation after completion, owner/pet task synchronization, and conflict detection for overlapping or duplicate scheduled times.

Confidence Level: 4/5 stars. The core scheduling logic is well covered by passing unit tests, but overall reliability would be stronger with broader edge-case, integration, and UI-level test coverage.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
