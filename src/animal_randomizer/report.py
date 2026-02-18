from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .models import ProjectModel


def _render_assignments_table(project: ProjectModel) -> str:
    lines = ["<table><thead><tr><th>Animal ID</th><th>Group</th></tr></thead><tbody>"]
    for row in project.assignments:
        lines.append(f"<tr><td>{row.animal_id}</td><td>{row.group}</td></tr>")
    lines.append("</tbody></table>")
    return "\n".join(lines)


def generate_html_report(project: ProjectModel, output_path: str | Path) -> Path:
    out = Path(output_path)
    now = datetime.now(timezone.utc).isoformat()

    group_cards = []
    for group, values in project.stats.get("groups", {}).items():
        group_cards.append(
            "<div class='card'>"
            f"<h3>{group}</h3>"
            f"<p>N={values.get('n')}</p>"
            f"<p>Weight mean={values.get('weight_mean')}</p>"
            f"<p>Weight SD={values.get('weight_sd')}</p>"
            f"<p>Sex={values.get('sex_distribution')}</p>"
            f"<p>Cage={values.get('cage_distribution')}</p>"
            "</div>"
        )

    warning_html = "".join(f"<li>{w}</li>" for w in project.warnings) or "<li>None</li>"
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
  <p>Study ID: {project.metadata.study_id}</p>
  <p>Title: {project.metadata.title}</p>
  <p>Researcher: {project.metadata.researcher_name}</p>
  <p>Institution: {project.metadata.institution}</p>
  <p>Method: {project.config.method}</p>
  <p>Seed: {project.config.seed}</p>
  <p>Generated: {now}</p>
  <h2>Integrity Hashes</h2>
  <p>Input hash: {project.hashes.get('input_hash')}</p>
  <p>Config hash: {project.hashes.get('config_hash')}</p>
  <p>Output hash: {project.hashes.get('output_hash')}</p>
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
