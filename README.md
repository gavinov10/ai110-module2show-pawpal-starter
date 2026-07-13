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

## ✨ Features

- **Priority sorting** — orders tasks high → low priority, breaking ties by shorter duration (`Scheduler.sort_tasks()`).
- **Sorting by time** — arranges tasks chronologically by their `HH:MM` time, with timeless tasks last (`Scheduler.sort_by_time()`).
- **Filtering by status** — show only completed or only incomplete tasks (`Scheduler.filter_by_status()`).
- **Filtering by pet** — pull just one pet's tasks by name (`Owner.tasks_for_pet()`).
- **Time-budget planning** — greedily fills the owner's available minutes with the highest-priority tasks and reports what was skipped (`Scheduler.filter_tasks()` + `generate_plan()`).
- **Conflict warnings** — detects overlapping time slots and returns non-fatal warning messages instead of crashing (`Scheduler.detect_conflicts()`).
- **Conflict resolution** — automatically shifts overlapping tasks to the next free slot so nothing is dropped (`Scheduler.resolve_conflicts()`).
- **Daily / weekly recurrence** — completing a recurring task auto-creates its next occurrence using `timedelta` (+1 day or +1 week) (`Task.next_occurrence()` + `Pet.complete_task()`).
- **Explainable plans** — every generated schedule can explain which tasks were scheduled or skipped and why (`Scheduler.explain()`).
- **Persistent Streamlit UI** — add pets/tasks, filter, mark complete, and generate schedules in the browser, with state kept across reruns via `st.session_state`.

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

### Main UI features (what a user can do)

Run the app with `streamlit run app.py`. The page lets a user:

- **Set the owner** and **add pets** (name + species) — each pet persists in the session.
- **Add tasks** to a selected pet with a title, duration, priority, preferred **time** (`HH:MM`), and **frequency** (daily / weekly / once).
- **Filter the task list** by status (All / Incomplete / Complete), displayed **sorted by time**.
- **Mark a task complete** — recurring tasks automatically spawn their next occurrence.
- **Generate a schedule** for the day, seeing conflict warnings, a suggested conflict-free timeline, the prioritized plan, and the reasoning behind it.

### Example workflow

1. Type an owner name (e.g. *Jordan*).
2. Add a pet — *Mochi* the cat — and click **Add pet**; it appears in the pets table.
3. Add a task: *Morning walk*, 30 min, high priority, `08:00`, daily → **Add task**.
4. Add a second, overlapping task: *Feeding*, 10 min, high, `08:15`, daily.
5. Set **Time available today** to 90 minutes and click **Generate schedule**.
6. PawPal+ shows a ⚠️ **conflict warning** (walk vs. feeding), a **resolved timeline** that shifts Feeding to 08:30, and **Today's Schedule** ordered by priority within the budget.
7. Back in Tasks, pick *Morning walk* and click **Complete task** — it's marked done and the next day's walk is auto-created.

### Key Scheduler behaviors shown

- **Sorting** — tasks display in chronological order even when added out of order.
- **Filtering** — the status toggle and per-pet views narrow the task list.
- **Conflict warnings + resolution** — overlaps are flagged, then auto-shifted to free slots.
- **Recurrence** — completing a daily/weekly task schedules the next occurrence.
- **Explainable planning** — the plan reports scheduled vs. skipped tasks and the time used.

### Sample CLI output (`python main.py`)

```
Tasks sorted by time
========================================
  08:00 — Morning walk (30 min)
  08:15 — Feeding (10 min)
  09:00 — Feeding (10 min)
  17:00 — Enrichment puzzle (20 min)
  18:00 — Grooming (25 min)

Open (incomplete) tasks
========================================
  [ ] Enrichment puzzle (20 min) [priority: low]
  [ ] Feeding (10 min) [priority: high]
  [ ] Grooming (25 min) [priority: medium]
  [ ] Feeding (10 min) [priority: high]

Whiskers' tasks only
========================================
  [ ] Grooming (25 min) [priority: medium]
  [ ] Feeding (10 min) [priority: high]

Conflict check
========================================
  ⚠️ Conflict: 'Morning walk' (08:00, 30 min) overlaps 'Feeding' (08:15, 10 min)

Resolved (conflict-free) timeline
========================================
  08:00 — Morning walk (30 min)
  08:30 — Feeding (10 min)
  09:00 — Feeding (10 min)
  17:00 — Enrichment puzzle (20 min)
  18:00 — Grooming (25 min)

Today's Schedule
========================================
  08:00 — Feeding (10 min) [priority: high]
  08:10 — Feeding (10 min) [priority: high]
  08:20 — Morning walk (30 min) [priority: high]
  08:50 — Grooming (25 min) [priority: medium]
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
