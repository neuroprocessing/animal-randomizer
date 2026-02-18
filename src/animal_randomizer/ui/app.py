from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QSplashScreen, QTextEdit, QVBoxLayout, QWidget

try:
    from .main_window import MainWindow
except ImportError:
    # Fallback for script-style execution contexts (e.g., some freeze runners).
    from animal_randomizer.ui.main_window import MainWindow


def _resource_path(relative_path: str) -> Path:
    """Resolve resource path for both source runs and PyInstaller bundles."""
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / relative_path
    return Path(__file__).resolve().parents[1] / "assets" / Path(relative_path).name


def _project_file_path(filename: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / filename
    return Path(__file__).resolve().parents[3] / filename


def _load_citation_text() -> str:
    citation_path = _project_file_path("CITATION.cff")
    if not citation_path.exists():
        return "CITATION.cff not found. Please cite via the GitHub CITATION.cff file."
    try:
        return citation_path.read_text(encoding="utf-8").strip()
    except OSError:
        return "Unable to read CITATION.cff. Please cite this software via repository metadata."


class WelcomeWindow(QWidget):
    def __init__(self, icon: QIcon, on_enter: Callable[[], None]) -> None:
        super().__init__()
        self._on_enter = on_enter
        self.setWindowTitle("Welcome - Neuroprocessing Randomizer")
        self.resize(900, 640)
        if not icon.isNull():
            self.setWindowIcon(icon)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("Neuroprocessing Randomizer")
        title.setStyleSheet("font-size:24px; font-weight:700; color:#6fddff;")
        subtitle = QLabel("Reproducible Animal Group Allocation")
        subtitle.setStyleSheet("font-size:14px; color:#9ec2d8;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        intro = QTextEdit()
        intro.setReadOnly(True)
        intro.setPlainText(
            "Welcome\n"
            "- Organization: Neuroprocessing (Open Neuroscience Systems Lab)\n"
            "- Team: Ali Mirzakhani + contributors\n"
            "- Support: https://github.com/neuroprocessing/animal-randomizer/issues\n"
            "- Repository: https://github.com/neuroprocessing/animal-randomizer\n\n"
            "How to cite\n"
            "The citation text below is loaded directly from CITATION.cff."
        )
        layout.addWidget(intro)

        citation = QTextEdit()
        citation.setReadOnly(True)
        citation.setPlainText(_load_citation_text())
        citation.setMinimumHeight(300)
        layout.addWidget(citation)

        enter_btn = QPushButton("Enter Application")
        enter_btn.setStyleSheet("font-weight:700; padding:10px;")
        enter_btn.clicked.connect(self._enter_app)
        layout.addWidget(enter_btn)

    def _enter_app(self) -> None:
        self._on_enter()
        self.close()


def launch() -> None:
    app = QApplication(sys.argv)

    logo_path = _resource_path("animal_randomizer/assets/logo.png")
    splash_path = _resource_path("animal_randomizer/assets/splash.png")

    if logo_path.exists():
        icon = QIcon(str(logo_path))
        app.setWindowIcon(icon)
    else:
        icon = QIcon()

    splash: QSplashScreen | None = None
    if splash_path.exists():
        pixmap = QPixmap(str(splash_path))
        if not pixmap.isNull():
            splash = QSplashScreen(pixmap)
            splash.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            splash.showMessage(
                "Neuroprocessing Randomizer v1.0.0",
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                QColor("#EAF8FF"),
            )
            splash.show()
            app.processEvents()

    main_window = MainWindow()
    if not icon.isNull():
        main_window.setWindowIcon(icon)

    welcome = WelcomeWindow(icon, on_enter=lambda: main_window.show())

    if splash is None:
        welcome.show()
    else:
        def _show_welcome() -> None:
            splash.finish(welcome)
            welcome.show()

        QTimer.singleShot(1200, _show_welcome)

    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
