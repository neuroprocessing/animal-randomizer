from __future__ import annotations

from typing import Iterable

from .models import AnimalRecord


def normalize_sex_value(value: str | None) -> str | None:
    """Normalize sex values to canonical form used across the project."""
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None

    lowered = cleaned.lower()
    if lowered in {"m", "male"}:
        return "M"
    if lowered in {"f", "female"}:
        return "F"
    if lowered in {"na", "n/a", "none", "unknown", "u", "-"}:
        return None
    raise ValueError(f"invalid sex value: {value}")


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
        try:
            animal.sex = normalize_sex_value(animal.sex)
        except ValueError:
            raise ValueError(f"Animal {animal.animal_id} has invalid sex value: {animal.sex}") from None
