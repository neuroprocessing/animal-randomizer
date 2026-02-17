from animal_randomizer.cli import generate_randomization


def test_reproducibility():
    df1 = generate_randomization(n=10, groups=2, seed=42)
    df2 = generate_randomization(n=10, groups=2, seed=42)
    assert df1.equals(df2)


def test_group_count():
    df = generate_randomization(n=12, groups=3, seed=1)
    assert df["Group"].nunique() == 3
