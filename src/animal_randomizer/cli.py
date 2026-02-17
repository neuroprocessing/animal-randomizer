import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import random


def generate_randomization(n: int, groups: int, seed: int, names=None, prefix="RAT", method="simple"):
    random.seed(seed)

    if names:
        group_names = names
    else:
        group_names = [f"Group {chr(65+i)}" for i in range(groups)]

    animals = [f"{prefix}_{i:03d}" for i in range(1, n + 1)]
    random.shuffle(animals)

    assignments = []
    for idx, animal in enumerate(animals):
        group = group_names[idx % groups]
        assignments.append(group)

    df = pd.DataFrame({
        "Animal_ID": animals,
        "Group": assignments,
        "Randomization_Seed": seed,
        "Method": method,
        "Timestamp": datetime.now().isoformat(timespec="seconds")
    })

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Animal Randomizer - reproducible random group assignment for animal studies."
    )
    parser.add_argument("--n", type=int, required=True, help="Number of animals")
    parser.add_argument("--groups", type=int, required=True, help="Number of groups")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for reproducibility")
    parser.add_argument("--out", type=str, default="randomization.csv", help="Output CSV file path")
    parser.add_argument("--names", type=str, default=None, help="Comma-separated group names")
    parser.add_argument("--prefix", type=str, default="RAT", help="Animal ID prefix (default: RAT)")
    parser.add_argument("--method", type=str, default="simple", help="Randomization method label")

    args = parser.parse_args()
    names = args.names.split(",") if args.names else None

    df = generate_randomization(
        n=args.n,
        groups=args.groups,
        seed=args.seed,
        names=names,
        prefix=args.prefix,
        method=args.method
    )

    out_path = Path(args.out)
    df.to_csv(out_path, index=False)

    print(f"[OK] Randomization saved to: {out_path.resolve()}")
    print(df.head())


if __name__ == "__main__":
    main()
