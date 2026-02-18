from animal_randomizer.randomization import randomize
from animal_randomizer.models import AnimalRecord, RandomizationConfig


def test_reproducibility():
    animals = [AnimalRecord(animal_id=f"RAT_{i:03d}") for i in range(10)]
    cfg = RandomizationConfig(method="simple", group_names=["A", "B"], seed=42)
    df1, _ = randomize(animals, cfg)
    df2, _ = randomize(animals, cfg)
    assert [(x.animal_id, x.group) for x in df1] == [(x.animal_id, x.group) for x in df2]


def test_group_count():
    animals = [AnimalRecord(animal_id=f"RAT_{i:03d}") for i in range(12)]
    cfg = RandomizationConfig(method="simple", group_names=["A", "B", "C"], seed=1)
    assignments, _ = randomize(animals, cfg)
    assert len(set(x.group for x in assignments)) == 3
