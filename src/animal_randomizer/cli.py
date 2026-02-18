from __future__ import annotations

import argparse
from pathlib import Path

from .io_handlers import export_assignments, import_animals
from .models import ConstraintConfig, ProjectModel, RandomizationConfig, StudyMetadata
from .project_io import save_project
from .report import generate_html_report
from .service import RandomizerService


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Neuroprocessing Randomizer CLI")
    p.add_argument("--input", required=True, help="Input CSV/XLSX animal file")
    p.add_argument("--study-id", required=True)
    p.add_argument("--title", default="Animal Study")
    p.add_argument("--researcher", default="Unknown")
    p.add_argument("--institution", default="Unknown")
    p.add_argument("--method", choices=["simple", "balanced", "stratified", "block"], default="balanced")
    p.add_argument("--groups", required=True, help="Comma-separated group names")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--stratify-by", default="", help="Comma-separated fields: sex,cage,weight,age")
    p.add_argument("--block-size", type=int, default=None)
    p.add_argument("--random-block-sizes", default="", help="e.g. 4,6,8")
    p.add_argument("--max-cage-per-group", type=int, default=None)
    p.add_argument("--no-minimize-cage", action="store_true")
    p.add_argument("--no-weight-balance", action="store_true")
    p.add_argument("--out-alloc", default="allocation.csv")
    p.add_argument("--out-report", default="allocation_report.html")
    p.add_argument("--out-project", default="study.nprj")
    return p


def main() -> None:
    args = build_parser().parse_args()
    animals = import_animals(args.input)

    group_names = [x.strip() for x in args.groups.split(",") if x.strip()]
    stratify_by = [x.strip() for x in args.stratify_by.split(",") if x.strip()]
    random_block_sizes = [int(x.strip()) for x in args.random_block_sizes.split(",") if x.strip()]

    cfg = RandomizationConfig(
        method=args.method,
        group_names=group_names,
        seed=args.seed,
        stratify_by=stratify_by,
        block_size=args.block_size,
        random_block_sizes=random_block_sizes,
        constraints=ConstraintConfig(
            max_animals_per_cage_per_group=args.max_cage_per_group,
            minimize_cage_clustering=not args.no_minimize_cage,
            weight_balance=not args.no_weight_balance,
        ),
    )
    meta = StudyMetadata(
        study_id=args.study_id,
        title=args.title,
        researcher_name=args.researcher,
        institution=args.institution,
    )
    project = ProjectModel(metadata=meta, animals=animals, config=cfg, groups=group_names)

    service = RandomizerService()
    artifacts = service.run(project)

    export_assignments(artifacts.assignments, args.out_alloc)
    generate_html_report(project, args.out_report)
    save_project(project, args.out_project)

    print(f"[OK] Randomization complete. Seed={artifacts.seed}")
    print(f"[OK] Allocation file: {Path(args.out_alloc).resolve()}")
    print(f"[OK] Report file: {Path(args.out_report).resolve()}")
    print(f"[OK] Project file: {Path(args.out_project).resolve()}")


if __name__ == "__main__":
    main()
