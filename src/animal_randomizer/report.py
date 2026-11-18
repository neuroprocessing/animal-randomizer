from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

from .models import ProjectModel


def _html(value: object) -> str:
    """Render arbitrary user/data content safely in an HTML report."""
    return escape("" if value is None else str(value), quote=True)


def _render_assignments_table(project: ProjectModel) -> str:
    lines = ["<table><thead><tr><th>Animal ID</th><th>Group</th></tr></thead><tbody>"]
    for row in project.assignments:
        lines.append(f"<tr><td>{_html(row.animal_id)}</td><td>{_html(row.group)}</td></tr>")
    lines.append("</tbody></table>")
    return "\n".join(lines)


def _build_methods_text(project: ProjectModel) -> str:
    cfg = project.config
    enabled_constraints: list[str] = []
    if cfg.constraints.max_animals_per_cage_per_group is not None:
        enabled_constraints.append(
            f"max {cfg.constraints.max_animals_per_cage_per_group} animal(s) per cage per group"
        )
    if cfg.constraints.minimize_cage_clustering:
        enabled_constraints.append("cage clustering minimization")
    if cfg.constraints.weight_balance:
        enabled_constraints.append("weight balancing")
    if cfg.stratify_by:
        enabled_constraints.append(f"stratification by {', '.join(cfg.stratify_by)}")
    constraints_text = "; ".join(enabled_constraints) if enabled_constraints else "no additional constraints"

    return (
        f"Animals were randomized into {len(cfg.group_names)} groups "
        f"({', '.join(cfg.group_names)}) using the {cfg.method} method "
        f"(algorithm version {cfg.algorithm_version}) with seed {cfg.seed}. "
        f"The configuration specified {constraints_text}; the exported allocation should be checked against "
        f"these constraints using the QC results before they are reported as achieved. "
        f"Reproducibility artifacts: input hash {project.hashes.get('input_hash')}, "
        f"config hash {project.hashes.get('config_hash')}, and output hash {project.hashes.get('output_hash')}. "
        f"Software version: {project.software_version}."
    )


def generate_html_report(project: ProjectModel, output_path: str | Path) -> Path:
    out = Path(output_path)
    now = datetime.now(timezone.utc).isoformat()

    group_cards = []
    for group, values in project.stats.get("groups", {}).items():
        group_cards.append(
            "<div class='card'>"
            f"<h3>{_html(group)}</h3>"
            f"<p>N={_html(values.get('n'))}</p>"
            f"<p>Weight mean={_html(values.get('weight_mean'))}</p>"
            f"<p>Weight SD={_html(values.get('weight_sd'))}</p>"
            f"<p>Sex={_html(values.get('sex_distribution'))}</p>"
            f"<p>Cage={_html(values.get('cage_distribution'))}</p>"
            "</div>"
        )

    warning_html = "".join(f"<li>{_html(w)}</li>" for w in project.warnings) or "<li>None</li>"
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Neuroprocessing Randomizer Report</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #081326; color: #e6f6ff; margin: 24px; }}
    h1, h2 {{ color: #50d6ff; }}
    table {{ border-collapse: collapse; width: 100%; background: #0f1e36; }}
    th, td {{ border: 1px solid #2a4d70; padding: 8px; text-align: left; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }}
    .card {{ background: #112442; padding: 12px; border-radius: 10px; }}
  </style>
</head>
<body>
  <h1>Neuroprocessing Randomizer</h1>
  <p><strong>Tagline:</strong> Reproducible Animal Group Allocation</p>
  <h2>Study Metadata</h2>
  <p>Study ID: {_html(project.metadata.study_id)}</p>
  <p>Title: {_html(project.metadata.title)}</p>
  <p>Researcher: {_html(project.metadata.researcher_name)}</p>
  <p>Institution: {_html(project.metadata.institution)}</p>
  <p>Method: {_html(project.config.method)}</p>
  <p>Seed: {_html(project.config.seed)}</p>
  <p>Generated: {_html(now)}</p>
  <h2>Integrity Hashes</h2>
  <p>Input hash: {_html(project.hashes.get('input_hash'))}</p>
  <p>Config hash: {_html(project.hashes.get('config_hash'))}</p>
  <p>Output hash: {_html(project.hashes.get('output_hash'))}</p>
  <h2>Methods-Ready Text</h2>
  <p>{_html(_build_methods_text(project))}</p>
  <h2>Assignments</h2>
  {_render_assignments_table(project)}
  <h2>Statistics</h2>
  <div class=\"grid\">{''.join(group_cards)}</div>
  <h2>Warnings</h2>
  <ul>{warning_html}</ul>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")
    return out
