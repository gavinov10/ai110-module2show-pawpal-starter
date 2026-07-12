"""Tests for core PawPal+ behaviors."""

from pawpal_system import Pet, Task


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
