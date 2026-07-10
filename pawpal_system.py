"""PawPal+ — core domain classes.

Skeleton only: names, attributes, and empty method stubs based on the UML
in diagrams/uml.mmd. Implement the logic in later phases.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, etc.)."""

    name: str
    duration: int  # minutes
    priority: str  # "high" | "medium" | "low"
    category: str = ""
    preferred_time: str = ""
    recurrence: str = "daily"  # "daily" | "weekly" | "once"

    def priority_score(self) -> int:
        """Return a sortable number derived from priority."""
        raise NotImplementedError

    def fits_in(self, remaining_minutes: int) -> bool:
        """Return True if this task fits in the time left."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a human-readable one-line summary of the task."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal being cared for, owning a list of care tasks."""

    name: str
    species: str = ""
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def edit_task(self, task_id: str) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner, holding constraints and one or more pets."""

    name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def set_availability(self, minutes: int) -> None:
        raise NotImplementedError

    def total_tasks(self) -> list[Task]:
        """Collect tasks across all of the owner's pets."""
        raise NotImplementedError


class Scheduler:
    """The scheduling engine: turns tasks + constraints into a daily plan."""

    def __init__(
        self,
        available_minutes: int,
        start_time: str = "08:00",
        tasks: list[Task] | None = None,
    ) -> None:
        self.available_minutes = available_minutes
        self.start_time = start_time
        self.tasks: list[Task] = tasks if tasks is not None else []

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority, then duration."""
        raise NotImplementedError

    def filter_tasks(self) -> list[Task]:
        """Drop tasks that don't fit in the remaining time."""
        raise NotImplementedError

    def resolve_conflicts(self) -> list[Task]:
        """Handle overlapping time slots."""
        raise NotImplementedError

    def generate_plan(self) -> list[Task]:
        """Produce the ordered daily plan."""
        raise NotImplementedError

    def explain(self) -> str:
        """Explain why tasks were included or skipped."""
        raise NotImplementedError
