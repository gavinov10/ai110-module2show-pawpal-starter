"""Tests for core PawPal+ behaviors."""

from datetime import timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = Task("Morning walk", 30, "high")
    assert task.completed is False  # starts incomplete

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Biscuit", species="Dog")
    assert len(pet.get_tasks()) == 0  # starts with no tasks

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.get_tasks()) == 1


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns tasks ordered by their HH:MM time."""
    # Added deliberately out of order.
    scheduler = Scheduler(
        available_minutes=120,
        tasks=[
            Task("Evening walk", 30, "low", time="17:00"),
            Task("Morning walk", 30, "high", time="08:00"),
            Task("Lunch", 15, "medium", time="12:00"),
        ],
    )

    ordered_times = [task.time for task in scheduler.sort_by_time()]

    assert ordered_times == ["08:00", "12:00", "17:00"]


def test_completing_daily_task_creates_next_day_occurrence():
    """Completing a daily task auto-creates a copy due the following day."""
    pet = Pet("Biscuit")
    daily = Task("Feeding", 10, "high", frequency="daily")
    pet.add_task(daily)

    new_task = pet.complete_task(daily.id)

    assert daily.completed is True                  # original is done
    assert new_task is not None                     # a new one was created
    assert new_task.completed is False              # the new one is pending
    assert new_task.due_date == daily.due_date + timedelta(days=1)
    assert len(pet.get_tasks()) == 2                # original + next occurrence


def test_detect_conflicts_flags_same_time_tasks():
    """detect_conflicts() warns when two tasks share the same time slot."""
    scheduler = Scheduler(
        available_minutes=120,
        tasks=[
            Task("Walk", 30, "high", time="08:00"),
            Task("Feeding", 10, "high", time="08:00"),  # exact same time
            Task("Nap", 20, "low", time="14:00"),        # no conflict
        ],
    )

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1                      # exactly one overlapping pair
    assert "Walk" in conflicts[0]
    assert "Feeding" in conflicts[0]
