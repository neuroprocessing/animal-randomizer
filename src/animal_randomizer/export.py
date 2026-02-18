"""Backward-compatible exports for export utilities."""

from .io_handlers import export_assignments
from .report import generate_html_report

__all__ = ["export_assignments", "generate_html_report"]
