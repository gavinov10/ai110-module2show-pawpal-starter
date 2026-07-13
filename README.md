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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Gavino
========================================
  08:00 — Feeding (10 min) [priority: high]
  08:10 — Feeding (10 min) [priority: high]
  08:20 — Morning walk (30 min) [priority: high]
  08:50 — Grooming (25 min) [priority: medium]

Time budget: 90 min
Scheduled 4 task(s), using 75 min:
  08:00 — Feeding (10 min) [priority: high]
  08:10 — Feeding (10 min) [priority: high]
  08:20 — Morning walk (30 min) [priority: high]
  08:50 — Grooming (25 min) [priority: medium]
Skipped 1 task(s) (not enough time):
  - Enrichment puzzle (20 min) [priority: low]
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`):

- **Task completion** — `mark_complete()` flips a task's status to done.
- **Task addition** — adding a task to a `Pet` increases its task count.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in
  chronological order even when added out of order.
- **Recurrence logic** — completing a `daily` task auto-creates a new task
  due the following day.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags two tasks
  scheduled at the same time.

Successful test run:

```
============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-9.1.1, pluggy-1.6.0
rootdir: .../ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 5 items

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.00s ===============================
```

**Confidence Level: ★★★★☆ (4/5)**

All five tests pass and cover the core scheduling behaviors (sorting,
recurrence, conflict detection) plus basic task management. Docking one star
because some edge cases aren't yet tested — empty pets/zero-minute budgets,
invalid time strings, and conflict *resolution* (`resolve_conflicts()`) — which
would be the next tests to add for full confidence.

## 📐 Smarter Scheduling

PawPal+ adds several layers of scheduling intelligence on top of the core
classes. Each feature and the method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting (priority) | `Scheduler.sort_tasks()` | High priority first, then shorter duration. |
| Task sorting (time) | `Scheduler.sort_by_time()` | Chronological by `"HH:MM"` time; timeless tasks go last. |
| Filtering by status | `Scheduler.filter_by_status()` | Show only complete or only incomplete tasks. |
| Filtering by pet | `Owner.tasks_for_pet()` | Return just one pet's tasks by name. |
| Budget filtering | `Scheduler.filter_tasks()` | Greedily keep tasks that fit the available minutes. |
| Conflict detection | `Scheduler.detect_conflicts()` | Returns non-fatal warning strings for overlapping time slots. |
| Conflict resolution | `Scheduler.resolve_conflicts()` | Shifts overlapping tasks to the next free slot (nothing dropped). |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next occurrence via `timedelta`. |
| Plan generation | `Scheduler.generate_plan()`, `Scheduler.explain()` | Builds a timed daily plan and explains what was scheduled/skipped. |

All of the above are exercised by the CLI demo in `main.py`
(`python main.py`).

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
