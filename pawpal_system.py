"""PawPal+ — core domain classes.

Implements the four main classes from the UML (diagrams/uml.mmd):
Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from itertools import combinations
from uuid import uuid4

# How far ahead the next occurrence of a recurring task is scheduled.
RECURRENCE_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}

# Priority label -> sortable weight (higher = more important).
PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""

    description: str
    duration: int  # minutes
    priority: str = "medium"  # "high" | "medium" | "low"
    time: str = ""  # preferred time of day, e.g. "morning" or "08:00"
    frequency: str = "daily"  # "daily" | "weekly" | "once"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    id: str = field(default_factory=lambda: uuid4().hex)

    def priority_score(self) -> int:
        """Return a sortable weight derived from priority (unknown -> 0)."""
        return PRIORITY_WEIGHTS.get(self.priority.lower(), 0)

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task fits in the time left."""
        return self.duration <= remaining_minutes

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, incomplete copy due next cycle (None if one-off).

        Uses timedelta to advance the due date: +1 day for "daily",
        +1 week for "weekly". A "once" task has no next occurrence.
        """
        delta = RECURRENCE_DELTA.get(self.frequency.lower())
        if delta is None:
            return None
        return replace(
            self,
            completed=False,
            due_date=self.due_date + delta,
            id=uuid4().hex,
        )

    def mark_incomplete(self) -> None:
        """Mark the task as not yet completed."""
        self.completed = False

    def summary(self) -> str:
        """Return a human-readable one-line summary of the task."""
        done = "✓" if self.completed else " "
        return f"[{done}] {self.description} ({self.duration} min) [priority: {self.priority}]"


@dataclass
class Pet:
    """An animal being cared for, owning a list of care tasks."""

    name: str
    species: str = ""
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def edit_task(self, task_id: str, **changes) -> Task | None:
        """Update fields on the task with the given id; return it (or None)."""
        task = self._find(task_id)
        if task is None:
            return None
        for attr, value in changes.items():
            if hasattr(task, attr):
                setattr(task, attr, value)
        return task

    def remove_task(self, task_id: str) -> bool:
        """Remove the task with the given id; return True if removed."""
        task = self._find(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True

    def complete_task(self, task_id: str) -> Task | None:
        """Mark a task complete; auto-add its next occurrence if recurring.

        Returns the newly created next-occurrence Task, or None if the
        task was one-off (or not found).
        """
        task = self._find(task_id)
        if task is None:
            return None
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            self.add_task(upcoming)
        return upcoming

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def _find(self, task_id: str) -> Task | None:
        return next((t for t in self.tasks if t.id == task_id), None)


@dataclass
class Owner:
    """The pet owner: holds constraints and manages multiple pets."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def set_availability(self, minutes: int) -> None:
        """Set how many minutes the owner has for care today."""
        self.available_minutes = minutes

    def total_tasks(self) -> list[Task]:
        """Collect tasks across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return the tasks belonging to the pet with the given name."""
        return [task for pet in self.pets if pet.name == pet_name
                for task in pet.get_tasks()]


class Scheduler:
    """The brain: retrieves, organizes, and schedules tasks across pets."""

    def __init__(
        self,
        available_minutes: int,
        start_time: str = "08:00",
        tasks: list[Task] | None = None,
    ) -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.tasks: list[Task] = tasks if tasks is not None else []
        # Populated by generate_plan(); used by explain().
        self.scheduled: list[tuple[str, Task]] = []
        self.skipped: list[Task] = []

    @classmethod
    def for_owner(cls, owner: Owner, start_time: str = "08:00") -> "Scheduler":
        """Build a scheduler from an owner's availability and pet tasks."""
        return cls(owner.available_minutes, start_time, owner.total_tasks())

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority (high first), then by shorter duration."""
        return sorted(
            self.tasks,
            key=lambda t: (-t.priority_score(), t.duration),
        )

    def sort_by_time(self) -> list[Task]:
        """Order tasks by their "HH:MM" time; timeless tasks go last.

        A "HH:MM" string sorts chronologically as plain text (e.g. "08:00"
        < "17:30"), so the lambda key just returns the time string, using
        "99:99" as a fallback so tasks with no time land at the end.
        """
        return sorted(self.tasks, key=lambda t: t.time or "99:99")

    def filter_by_status(self, completed: bool = False) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.completed == completed]

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for tasks whose time slots overlap.

        Lightweight and non-fatal: tasks without a valid "HH:MM" time are
        skipped, and overlaps are reported as strings rather than raised
        as errors. Two tasks conflict when one starts before the other ends.
        """
        # Build (start_minute, end_minute, task) for tasks with a valid time.
        timed: list[tuple[int, int, Task]] = []
        for task in self.tasks:
            start = self._to_minutes(task.time)
            if start is not None:
                timed.append((start, start + task.duration, task))

        warnings: list[str] = []
        for (start_a, end_a, task_a), (start_b, end_b, task_b) in combinations(timed, 2):
            # Overlap when each starts before the other ends.
            if start_a < end_b and start_b < end_a:
                warnings.append(
                    f"⚠️ Conflict: '{task_a.description}' ({task_a.time}, "
                    f"{task_a.duration} min) overlaps '{task_b.description}' "
                    f"({task_b.time}, {task_b.duration} min)"
                )
        return warnings

    def resolve_conflicts(self) -> list[tuple[str, Task]]:
        """Return a conflict-free plan by shifting overlapping tasks later.

        Each task is placed at its preferred time when that slot is free;
        if it would overlap a task already placed, it is pushed to start
        when the previous one ends. Timeless tasks are appended after the
        timed ones. Nothing is dropped.
        """
        timed: list[tuple[int, Task]] = []
        timeless: list[Task] = []
        for task in self.tasks:
            start = self._to_minutes(task.time)
            (timeless if start is None else timed).append(
                task if start is None else (start, task)
            )

        # Earlier preferred start first; for ties, higher priority wins.
        timed.sort(key=lambda pair: (pair[0], -pair[1].priority_score()))

        plan: list[tuple[str, Task]] = []
        cursor = 0  # minutes since midnight of the earliest free slot
        for start, task in timed:
            actual = max(start, cursor)
            plan.append((self._from_minutes(actual), task))
            cursor = actual + task.duration
        for task in timeless:
            plan.append((self._from_minutes(cursor), task))
            cursor += task.duration
        return plan

    @staticmethod
    def _to_minutes(time_str: str) -> int | None:
        """Convert an 'HH:MM' string to minutes since midnight (None if invalid)."""
        try:
            clock = datetime.strptime(time_str, "%H:%M")
        except (ValueError, TypeError):
            return None
        return clock.hour * 60 + clock.minute

    @staticmethod
    def _from_minutes(total: int) -> str:
        """Convert minutes since midnight back to an 'HH:MM' string."""
        return f"{total // 60 % 24:02d}:{total % 60:02d}"

    def filter_tasks(self) -> list[Task]:
        """Keep only the tasks that fit within the available time budget."""
        remaining = self.available_minutes
        kept: list[Task] = []
        for task in self.sort_tasks():
            if task.fits_in(remaining):
                kept.append(task)
                remaining -= task.duration
        return kept

    def generate_plan(self) -> list[tuple[str, Task]]:
        """Produce an ordered daily plan of (start_time, task) entries.

        Tasks are scheduled back-to-back from start_time; any that don't
        fit in the time budget are recorded in self.skipped.
        """
        chosen = self.filter_tasks()
        chosen_ids = {t.id for t in chosen}
        self.skipped = [t for t in self.tasks if t.id not in chosen_ids]

        clock = datetime.strptime(self.start_time, "%H:%M")
        plan: list[tuple[str, Task]] = []
        for task in chosen:
            plan.append((clock.strftime("%H:%M"), task))
            clock += timedelta(minutes=task.duration)

        self.scheduled = plan
        return plan

    def explain(self) -> str:
        """Explain which tasks were scheduled and which were skipped."""
        if not self.scheduled and not self.skipped:
            self.generate_plan()

        lines = [f"Time budget: {self.available_minutes} min"]
        used = sum(task.duration for _, task in self.scheduled)
        lines.append(f"Scheduled {len(self.scheduled)} task(s), using {used} min:")
        for start, task in self.scheduled:
            lines.append(f"  {start} — {task.description} ({task.duration} min)"
                         f" [priority: {task.priority}]")
        if self.skipped:
            lines.append(f"Skipped {len(self.skipped)} task(s) (not enough time):")
            for task in self.skipped:
                lines.append(f"  - {task.description} ({task.duration} min)"
                             f" [priority: {task.priority}]")
        return "\n".join(lines)
