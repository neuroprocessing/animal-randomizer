from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .models import AnimalRecord, AssignmentRecord


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
                sex=(None if pd.isna(row.get("Sex")) else str(row.get("Sex"))),
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


def export_assignments(assignments: List[AssignmentRecord], path: str | Path) -> None:
    frame = pd.DataFrame([asdict(x) for x in assignments])
    path = Path(path)
    if path.suffix.lower() == ".csv":
        frame.to_csv(path, index=False)
    elif path.suffix.lower() == ".xlsx":
        frame.to_excel(path, index=False)
    else:
        raise ValueError("Export format must be .csv or .xlsx")


def assignments_to_dict(assignments: List[AssignmentRecord]) -> List[Dict[str, Any]]:
    return [asdict(a) for a in assignments]
