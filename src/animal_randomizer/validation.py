from __future__ import annotations

from typing import Iterable

from .models import AnimalRecord


VALID_SEX = {"M", "F", "Male", "Female", None, ""}


def validate_animals(animals: Iterable[AnimalRecord]) -> None:
    seen: set[str] = set()
    for idx, animal in enumerate(animals, start=1):
        if not animal.animal_id:
            raise ValueError(f"Animal at row {idx} has empty Animal ID")
        if animal.animal_id in seen:
            raise ValueError(f"Duplicate Animal ID detected: {animal.animal_id}")
        seen.add(animal.animal_id)
        if animal.weight is not None and animal.weight <= 0:
            raise ValueError(f"Animal {animal.animal_id} has non-positive weight")
        if animal.sex not in VALID_SEX:
            raise ValueError(f"Animal {animal.animal_id} has invalid sex value: {animal.sex}")
