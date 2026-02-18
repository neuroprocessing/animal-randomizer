from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .models import AnimalRecord, AssignmentRecord
from .validation import normalize_sex_value


def animals_from_dataframe(df: pd.DataFrame) -> List[AnimalRecord]:
    required = {"Animal ID", "Animal_ID", "animal_id"}
    available = set(df.columns)
    col = next((c for c in required if c in available), None)
    if col is None:
        raise ValueError("Input file must include an Animal ID column")

    rows: List[AnimalRecord] = []
    for _, row in df.iterrows():
        rows.append(
            AnimalRecord(
                animal_id=str(row.get(col, "")).strip(),
                sex=(
                    None
                    if pd.isna(row.get("Sex"))
                    else normalize_sex_value(str(row.get("Sex")))
                ),
                weight=(None if pd.isna(row.get("Weight")) else float(row.get("Weight"))),
                age=(None if pd.isna(row.get("Age")) else float(row.get("Age"))),
                cage=(None if pd.isna(row.get("Cage")) else str(row.get("Cage"))),
                strain=(None if pd.isna(row.get("Strain")) else str(row.get("Strain"))),
                species=(None if pd.isna(row.get("Species")) else str(row.get("Species"))),
                notes=(None if pd.isna(row.get("Condition/Notes")) else str(row.get("Condition/Notes"))),
                source=(None if pd.isna(row.get("Source")) else str(row.get("Source"))),
                date_of_arrival=(None if pd.isna(row.get("Date of arrival")) else str(row.get("Date of arrival"))),
            )
        )
    return rows


def import_animals(path: str | Path) -> List[AnimalRecord]:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Only CSV and Excel imports are supported")
    return animals_from_dataframe(df)


def build_allocation_dataframe(
    assignments: List[AssignmentRecord], animals: List[AnimalRecord] | None = None
) -> pd.DataFrame:
    base = pd.DataFrame([asdict(x) for x in assignments]).rename(
        columns={"animal_id": "Animal_ID", "group": "Group"}
    )
    if not animals:
        return base

    meta = pd.DataFrame(
        [
            {
                "Animal_ID": a.animal_id,
                "Sex": a.sex,
                "Weight": a.weight,
                "Age": a.age,
                "Cage": a.cage,
                "Strain": a.strain,
                "Species": a.species,
                "Notes": a.notes,
                "Source": a.source,
                "Date_of_arrival": a.date_of_arrival,
            }
            for a in animals
        ]
    )
    merged = base.merge(meta, on="Animal_ID", how="left")
    return merged


def export_assignments(
    assignments: List[AssignmentRecord],
    path: str | Path,
    animals: List[AnimalRecord] | None = None,
) -> None:
    frame = build_allocation_dataframe(assignments, animals)
    path = Path(path)
    if path.suffix.lower() == ".csv":
        frame.to_csv(path, index=False, encoding="utf-8-sig")
    elif path.suffix.lower() == ".xlsx":
        frame.to_excel(path, index=False)
    elif path.suffix.lower() in {".tsv", ".txt"}:
        frame.to_csv(path, index=False, sep="\t", encoding="utf-8")
    else:
        raise ValueError("Export format must be .csv, .xlsx, .tsv, or .txt")


def assignments_to_dict(assignments: List[AssignmentRecord]) -> List[Dict[str, Any]]:
    return [asdict(a) for a in assignments]


def export_interop_bundle(
    assignments: List[AssignmentRecord],
    animals: List[AnimalRecord],
    output_dir: str | Path,
    stem: str = "allocation",
) -> Dict[str, Path]:
    """
    Export an interoperability bundle suitable for Excel, Prism, and Origin.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    long_df = build_allocation_dataframe(assignments, animals)
    long_df = long_df.sort_values(["Group", "Animal_ID"]).reset_index(drop=True)

    csv_path = output_dir / f"{stem}.csv"
    xlsx_path = output_dir / f"{stem}.xlsx"
    tsv_path = output_dir / f"{stem}.tsv"
    prism_grouped_path = output_dir / f"{stem}_grouped_for_prism.csv"
    weights_grouped_path = output_dir / f"{stem}_weights_for_prism.csv"

    long_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    long_df.to_excel(xlsx_path, index=False)
    long_df.to_csv(tsv_path, index=False, sep="\t", encoding="utf-8")

    grouped_ids = (
        long_df[["Animal_ID", "Group"]]
        .assign(idx=lambda d: d.groupby("Group").cumcount())
        .pivot(index="idx", columns="Group", values="Animal_ID")
        .reset_index(drop=True)
    )
    grouped_ids.to_csv(prism_grouped_path, index=False, encoding="utf-8-sig")

    if "Weight" in long_df.columns:
        valid_weights = long_df.dropna(subset=["Weight"])
        if not valid_weights.empty:
            grouped_weights = (
                valid_weights[["Weight", "Group"]]
                .assign(idx=lambda d: d.groupby("Group").cumcount())
                .pivot(index="idx", columns="Group", values="Weight")
                .reset_index(drop=True)
            )
            grouped_weights.to_csv(weights_grouped_path, index=False, encoding="utf-8-sig")

    return {
        "csv": csv_path,
        "xlsx": xlsx_path,
        "tsv": tsv_path,
        "prism_grouped": prism_grouped_path,
        "prism_weights_grouped": weights_grouped_path,
    }
