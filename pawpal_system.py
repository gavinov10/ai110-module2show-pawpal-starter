"""PawPal+ — core domain classes.

Implements the four main classes from the UML (diagrams/uml.mmd):
Task, Pet, Owner, and Scheduler.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4

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
