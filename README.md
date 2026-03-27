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

## Smarter Scheduling

The scheduler now does more than just list tasks. It can track task status, sort tasks by priority or scheduled time, detect overlapping tasks, and flag conflicts for the same pet or across different pets. The system also keeps task selection within the owner's available time and can explain why a daily plan was chosen.

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
