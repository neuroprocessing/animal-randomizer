from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..io_handlers import export_assignments, export_interop_bundle, import_animals
from ..models import AnimalRecord, ConstraintConfig, ProjectModel, RandomizationConfig, StudyMetadata
from ..project_io import save_project
from ..report import generate_html_report
from ..service import RandomizerService
from ..validation import normalize_sex_value


class ExportSummaryDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None,
        method: str,
        output_dir: Path,
        files: list[tuple[str, Path]],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export Summary")
        self.resize(820, 620)

        layout = QVBoxLayout(self)

        title = QLabel("Successfully Exported")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Output directory: {output_dir}"))

        info = QTextBrowser()
        info.setOpenExternalLinks(True)
        info.setHtml(self._build_html(method, files))
        layout.addWidget(info)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _build_html(self, method: str, files: list[tuple[str, Path]]) -> str:
        files_html = "".join(
            f"<li><b>{label}</b>: <code>{path.name}</code></li>" for label, path in files
        )
        method_help = self._article_guidance(method)

        return f"""
        <h3>Generated Files</h3>
        <ul>{files_html}</ul>

        <h3>File Type Help</h3>
        <ul>
          <li><b>CSV/XLSX</b>: primary allocation tables for Excel and lab records.</li>
          <li><b>TSV</b>: tab-delimited format for Origin and generic analysis pipelines.</li>
          <li><b>Prism grouped CSVs</b>: direct group-wise import for GraphPad Prism analysis/plots.</li>
          <li><b>HTML report</b>: human-readable summary with seed, hashes, assignments, and warnings.</li>
          <li><b>.nprj</b>: full reproducibility snapshot (metadata, config, logs, results).</li>
        </ul>

        <h3>How to Use in Article (Method-Specific)</h3>
        <p>{method_help}</p>
        <p>
          Recommended manuscript elements: randomization method, constraints, seed,
          software version, algorithm version, and integrity hashes from the report.
        </p>
        """

    def _article_guidance(self, method: str) -> str:
        m = method.lower().strip()
        if m == "simple":
            return (
                "Animals were allocated using simple randomization with a fixed seed. "
                "Report the seed and software version to ensure reproducibility."
            )
        if m == "balanced":
            return (
                "Animals were allocated using balanced randomization to maintain near-equal "
                "group sizes while preserving randomness."
            )
        if m == "stratified":
            return (
                "Animals were allocated using stratified randomization across selected factors "
                "(e.g., sex/cage/weight/age) to reduce confounding imbalance."
            )
        if m == "block":
            return (
                "Animals were allocated using block randomization with configured block size rules "
                "to maintain temporal/allocation balance."
            )
        return (
            "Animals were allocated using a reproducible randomization workflow with documented "
            "configuration, seed, and integrity checks."
        )


class MainWindow(QMainWindow):
    SEX_OPTIONS = ["", "M", "F", "Male", "Female", "NA", "Unknown"]
    SPECIES_OPTIONS = ["", "Rat", "Mouse", "Other"]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Neuroprocessing Randomizer")
        self.resize(1320, 820)

        self.dark = True
        self.animals: list[AnimalRecord] = []
        self.project: ProjectModel | None = None

        self.step_titles = [
            "1. Create Study",
            "2. Import Animals",
            "3. Configure Strategy",
            "4. Run Randomization",
            "5. Review and Export",
        ]

        self._setup_fonts()
        self._build_layout()

        self.statusBar().showMessage("Ready")
        self.apply_theme()
        self._set_step(0)

    def _setup_fonts(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        app.setFont(QFont("Segoe UI", 10))

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(14)

        self.sidebar = self._build_sidebar()

        content_shell = QWidget()
        content_layout = QVBoxLayout(content_shell)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        self.header_title = QLabel("Neuroprocessing Randomizer")
        self.header_title.setObjectName("pageHeader")
        self.header_subtitle = QLabel("Reproducible Animal Group Allocation")
        self.header_subtitle.setObjectName("pageSubHeader")

        header_row = QWidget()
        header_layout = QVBoxLayout(header_row)
        header_layout.setContentsMargins(6, 2, 6, 2)
        header_layout.addWidget(self.header_title)
        header_layout.addWidget(self.header_subtitle)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_study_page())
        self.pages.addWidget(self._build_animals_page())
        self.pages.addWidget(self._build_config_page())
        self.pages.addWidget(self._build_run_page())
        self.pages.addWidget(self._build_results_page())

        nav_bar = self._build_nav_bar()

        content_layout.addWidget(header_row)
        content_layout.addWidget(self.pages)
        content_layout.addWidget(nav_bar)

        root_layout.addWidget(self.sidebar, 1)
        root_layout.addWidget(content_shell, 4)

        self.setCentralWidget(root)

    def _card(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        return frame

    def _build_sidebar(self) -> QWidget:
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = QLabel("Neuroprocessing")
        title.setObjectName("navTitle")
        subtitle = QLabel("Animal Randomizer v1.0.0")
        subtitle.setObjectName("navSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.step_buttons: list[QPushButton] = []
        for idx, name in enumerate(self.step_titles):
            btn = QPushButton(name)
            btn.setObjectName("stepButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked=False, i=idx: self._set_step(i))
            self.step_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        info = QLabel(
            "Scientific Workflow\n"
            "- Reproducible seeds\n"
            "- Bias-aware constraints\n"
            "- Audit-grade exports"
        )
        info.setObjectName("smallInfo")
        layout.addWidget(info)
        return card

    def _build_nav_bar(self) -> QWidget:
        wrap = self._card()
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(12, 10, 12, 10)

        self.theme_btn = QPushButton("Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.help_btn = QPushButton("Help")
        self.help_btn.clicked.connect(self.show_help_dialog)
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.prev_btn.clicked.connect(self._go_prev)
        self.next_btn.clicked.connect(self._go_next)

        layout.addWidget(self.theme_btn)
        layout.addWidget(self.help_btn)
        layout.addStretch()
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        return wrap

    def _build_section_header(self, title: str, subtitle: str) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 6)
        t = QLabel(title)
        t.setObjectName("sectionTitle")
        s = QLabel(subtitle)
        s.setObjectName("sectionSubtitle")
        layout.addWidget(t)
        layout.addWidget(s)
        return wrap

    def _build_study_page(self) -> QWidget:
        page = self._card()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(self._build_section_header("Create Study", "Define study identity and operator metadata."))

        welcome = QTextBrowser()
        welcome.setOpenExternalLinks(True)
        welcome.setMaximumHeight(220)
        welcome.setHtml(
            """
            <h3 style="margin:0 0 6px 0;">Welcome to Neuroprocessing Randomizer</h3>
            <p style="margin:0 0 10px 0;">
              <b>Reproducible Animal Group Allocation</b> for neuroscience and preclinical workflows.
            </p>
            <p style="margin:0 0 8px 0;"><b>Team</b><br/>
              Neuroprocessing Open Neuroscience Systems Lab<br/>
              Maintainer: Ali Mirzakhani + contributors
            </p>
            <p style="margin:0 0 8px 0;"><b>How to Cite</b><br/>
              Please cite this tool in publications using the
              <a href="https://github.com/neuroprocessing/animal-randomizer/blob/main/CITATION.cff">CITATION.cff file</a>.
            </p>
            <p style="margin:0;"><b>Support the Project</b><br/>
              Report issues and request features on
              <a href="https://github.com/neuroprocessing/animal-randomizer/issues">GitHub Issues</a>,
              or contribute code via pull requests at
              <a href="https://github.com/neuroprocessing/animal-randomizer">the repository</a>.
            </p>
            """
        )
        layout.addWidget(welcome)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(12)

        self.study_id = QLineEdit("NP-001")
        self.study_title = QLineEdit("Pilot Study")
        self.researcher = QLineEdit("Researcher")
        self.institution = QLineEdit("Institution")
        form.addRow("Study ID", self.study_id)
        form.addRow("Title", self.study_title)
        form.addRow("Researcher", self.researcher)
        form.addRow("Institution", self.institution)

        layout.addLayout(form)
        layout.addStretch()
        return page

    def _build_animals_page(self) -> QWidget:
        page = self._card()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(self._build_section_header("Import or Add Animals", "Load CSV/XLSX or manually edit records."))

        auto_box = self._card()
        auto_layout = QGridLayout(auto_box)
        auto_layout.setContentsMargins(12, 12, 12, 12)
        auto_layout.setHorizontalSpacing(12)
        auto_layout.setVerticalSpacing(8)

        self.auto_count = QSpinBox()
        self.auto_count.setRange(1, 5000)
        self.auto_count.setValue(24)
        self.auto_prefix = QLineEdit("RAT")
        self.auto_start = QSpinBox()
        self.auto_start.setRange(1, 999999)
        self.auto_start.setValue(1)
        self.auto_pad = QSpinBox()
        self.auto_pad.setRange(1, 6)
        self.auto_pad.setValue(3)
        self.auto_species = QComboBox()
        self.auto_species.addItems(["Rat", "Mouse", "Other"])
        self.auto_sex_mode = QComboBox()
        self.auto_sex_mode.addItems(["Alternating M/F", "All Male", "All Female", "Unknown"])
        self.auto_strain = QLineEdit("")
        self.auto_source = QLineEdit("")
        self.auto_cage = QLineEdit("")
        self.auto_arrival = QDateEdit()
        self.auto_arrival.setCalendarPopup(True)
        self.auto_arrival.setDisplayFormat("yyyy-MM-dd")
        self.auto_arrival.setDate(QDate.currentDate())
        self.auto_replace = QCheckBox("Replace existing table")
        self.auto_replace.setChecked(True)
        self.auto_generate_btn = QPushButton("Auto Generate Animal List")
        self.auto_generate_btn.clicked.connect(self.generate_auto_animals)

        auto_layout.addWidget(QLabel("Number of Animals"), 0, 0)
        auto_layout.addWidget(self.auto_count, 0, 1)
        auto_layout.addWidget(QLabel("ID Prefix"), 0, 2)
        auto_layout.addWidget(self.auto_prefix, 0, 3)
        auto_layout.addWidget(QLabel("Start Number"), 1, 0)
        auto_layout.addWidget(self.auto_start, 1, 1)
        auto_layout.addWidget(QLabel("ID Zero Padding"), 1, 2)
        auto_layout.addWidget(self.auto_pad, 1, 3)
        auto_layout.addWidget(QLabel("Species"), 2, 0)
        auto_layout.addWidget(self.auto_species, 2, 1)
        auto_layout.addWidget(QLabel("Sex Pattern"), 2, 2)
        auto_layout.addWidget(self.auto_sex_mode, 2, 3)
        auto_layout.addWidget(QLabel("Default Strain"), 3, 0)
        auto_layout.addWidget(self.auto_strain, 3, 1)
        auto_layout.addWidget(QLabel("Default Source"), 3, 2)
        auto_layout.addWidget(self.auto_source, 3, 3)
        auto_layout.addWidget(QLabel("Default Cage"), 4, 0)
        auto_layout.addWidget(self.auto_cage, 4, 1)
        auto_layout.addWidget(QLabel("Date of Arrival"), 4, 2)
        auto_layout.addWidget(self.auto_arrival, 4, 3)
        auto_layout.addWidget(self.auto_replace, 5, 0, 1, 2)
        auto_layout.addWidget(self.auto_generate_btn, 5, 2, 1, 2)
        layout.addWidget(auto_box)

        buttons = QHBoxLayout()
        self.import_btn = QPushButton("Import CSV/XLSX")
        self.add_row_btn = QPushButton("Add Animal")
        self.import_btn.clicked.connect(self.import_animals_file)
        self.add_row_btn.clicked.connect(self.add_animal_row)
        buttons.addWidget(self.import_btn)
        buttons.addWidget(self.add_row_btn)
        buttons.addStretch()
        layout.addLayout(buttons)

        self.animals_table = QTableWidget()
        self.animal_columns = [
            "Animal ID",
            "Sex",
            "Weight",
            "Age",
            "Cage",
            "Strain",
            "Species",
            "Condition/Notes",
            "Source",
            "Date of arrival",
        ]
        self.animals_table.setColumnCount(len(self.animal_columns))
        self.animals_table.setHorizontalHeaderLabels(self.animal_columns)
        self.animals_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.animals_table)
        return page

    def _build_config_page(self) -> QWidget:
        page = self._card()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(self._build_section_header("Configure Strategy", "Set groups, method, seed, and balancing constraints."))

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        self.groups = QLineEdit("Control,Treatment")
        self.groups.setPlaceholderText("Example: Control,DrugA,DrugB")
        self.groups.setToolTip("Comma-separated group names used for allocation.")
        self.method = QComboBox()
        self.method.addItems(["simple", "balanced", "stratified", "block"])
        self.method.setToolTip("balanced is usually the safest default.")
        self.seed = QLineEdit("")
        self.seed.setPlaceholderText("Optional integer seed, e.g. 20260218")
        self.seed.setToolTip("Same seed + same input = same assignments.")
        self.stratify_by = QLineEdit("sex,cage,weight")
        self.stratify_by.setPlaceholderText("sex,cage,weight")
        self.stratify_by.setToolTip("Allowed fields: sex,cage,weight,age")
        self.block_size = QSpinBox()
        self.block_size.setRange(0, 500)
        self.block_size.setToolTip("0 disables fixed block mode.")
        self.random_block_sizes = QLineEdit("4,6,8")
        self.random_block_sizes.setPlaceholderText("4,6,8")
        self.random_block_sizes.setToolTip("Comma-separated integer block sizes.")
        self.max_cage = QSpinBox()
        self.max_cage.setRange(0, 20)
        self.max_cage.setValue(1)
        self.max_cage.setToolTip("0 disables this cage limit.")
        self.minimize_cage = QCheckBox("Minimize cage clustering")
        self.minimize_cage.setChecked(True)
        self.minimize_cage.setToolTip("Distributes animals from same cage across groups.")
        self.weight_balance = QCheckBox("Enable weight balancing")
        self.weight_balance.setChecked(True)
        self.weight_balance.setToolTip("Balances weight bins to reduce confounding.")

        grid.addWidget(QLabel("Group Names"), 0, 0)
        grid.addWidget(self.groups, 0, 1)
        grid.addWidget(QLabel("Method"), 1, 0)
        grid.addWidget(self.method, 1, 1)
        grid.addWidget(QLabel("Seed (optional)"), 2, 0)
        grid.addWidget(self.seed, 2, 1)
        grid.addWidget(QLabel("Stratify By"), 3, 0)
        grid.addWidget(self.stratify_by, 3, 1)
        grid.addWidget(QLabel("Fixed Block Size (0=off)"), 4, 0)
        grid.addWidget(self.block_size, 4, 1)
        grid.addWidget(QLabel("Random Block Sizes"), 5, 0)
        grid.addWidget(self.random_block_sizes, 5, 1)
        grid.addWidget(QLabel("Max per Cage per Group (0=off)"), 6, 0)
        grid.addWidget(self.max_cage, 6, 1)
        grid.addWidget(self.minimize_cage, 7, 1)
        grid.addWidget(self.weight_balance, 8, 1)

        layout.addLayout(grid)
        layout.addStretch()
        return page

    def _build_run_page(self) -> QWidget:
        page = self._card()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(self._build_section_header("Run Randomization", "Generate allocation, hashes, and validation warnings."))

        self.run_btn = QPushButton("Run Randomization")
        self.run_btn.clicked.connect(self.run_randomization)
        layout.addWidget(self.run_btn)

        self.run_summary = QTextEdit()
        self.run_summary.setReadOnly(True)
        layout.addWidget(self.run_summary)
        return page

    def _build_results_page(self) -> QWidget:
        page = self._card()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)

        layout.addWidget(self._build_section_header("Review and Export", "Inspect assignments and export all study artifacts."))

        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(2)
        self.assignments_table.setHorizontalHeaderLabels(["Animal ID", "Group"])
        self.assignments_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.assignments_table)

        actions = QHBoxLayout()
        self.export_btn = QPushButton("Export Allocation + Report + Project")
        self.export_btn.clicked.connect(self.export_outputs)
        actions.addWidget(self.export_btn)
        actions.addStretch()
        layout.addLayout(actions)
        return page

    def apply_theme(self) -> None:
        if self.dark:
            self.setStyleSheet(
                """
                QWidget { background: #061023; color: #eaf8ff; font-size: 13px; }
                QFrame#card { background: #0c1b34; border: 1px solid #1f4064; border-radius: 14px; }
                #pageHeader { font-size: 21px; font-weight: 700; color: #6fddff; }
                #pageSubHeader { color: #98c9e5; font-size: 12px; }
                #navTitle { font-size: 18px; font-weight: 700; color: #6fddff; }
                #navSubtitle { color: #8fb8d1; font-size: 12px; margin-bottom: 8px; }
                #sectionTitle { font-size: 17px; font-weight: 700; color: #dff6ff; }
                #sectionSubtitle { color: #9ec2d8; margin-bottom: 6px; }
                #smallInfo { color: #9ec2d8; font-size: 12px; line-height: 1.5; }

                QLineEdit, QComboBox, QSpinBox, QTableWidget, QTextEdit {
                    background: #0a162d;
                    border: 1px solid #2c5b88;
                    border-radius: 8px;
                    padding: 6px;
                    selection-background-color: #22c8f0;
                    selection-color: #021422;
                }

                QPushButton {
                    background: #22c8f0;
                    color: #021422;
                    border: 0;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 700;
                }
                QPushButton:hover { background: #6fddff; }
                QPushButton:pressed { background: #19a7cc; }
                QPushButton:checked { background: #6fddff; }
                QPushButton#stepButton {
                    background: #0b1a33;
                    color: #b8d5e6;
                    border: 1px solid #26496e;
                    text-align: left;
                    padding: 10px;
                }
                QPushButton#stepButton:checked {
                    background: #143056;
                    color: #e9f8ff;
                    border: 1px solid #22c8f0;
                }
                QHeaderView::section {
                    background: #102447;
                    color: #d8f0ff;
                    border: 0;
                    border-bottom: 1px solid #2e5e8d;
                    padding: 6px;
                    font-weight: 600;
                }
                QStatusBar { background: #09162d; color: #8fb8d1; }
                """
            )
        else:
            self.setStyleSheet(
                """
                QWidget { background: #f4f9ff; color: #12314f; font-size: 13px; }
                QFrame#card { background: #ffffff; border: 1px solid #c2d9ea; border-radius: 14px; }
                #pageHeader { font-size: 21px; font-weight: 700; color: #0d7195; }
                #pageSubHeader { color: #4b7895; font-size: 12px; }
                #navTitle { font-size: 18px; font-weight: 700; color: #0d7195; }
                #navSubtitle { color: #4b7895; font-size: 12px; margin-bottom: 8px; }
                #sectionTitle { font-size: 17px; font-weight: 700; color: #163a59; }
                #sectionSubtitle { color: #557c98; margin-bottom: 6px; }
                #smallInfo { color: #557c98; font-size: 12px; line-height: 1.5; }

                QLineEdit, QComboBox, QSpinBox, QTableWidget, QTextEdit {
                    background: #ffffff;
                    border: 1px solid #adc9dc;
                    border-radius: 8px;
                    padding: 6px;
                    selection-background-color: #0bb4df;
                    selection-color: #ffffff;
                }

                QPushButton {
                    background: #0d8fb2;
                    color: #ffffff;
                    border: 0;
                    border-radius: 9px;
                    padding: 8px 12px;
                    font-weight: 700;
                }
                QPushButton:hover { background: #0bb4df; }
                QPushButton:pressed { background: #0a7391; }
                QPushButton:checked { background: #0bb4df; }
                QPushButton#stepButton {
                    background: #eff7fd;
                    color: #2f5874;
                    border: 1px solid #c4dcec;
                    text-align: left;
                    padding: 10px;
                }
                QPushButton#stepButton:checked {
                    background: #dff3fc;
                    color: #123a55;
                    border: 1px solid #0bb4df;
                }
                QHeaderView::section {
                    background: #e9f4fb;
                    color: #214c69;
                    border: 0;
                    border-bottom: 1px solid #c4dcec;
                    padding: 6px;
                    font-weight: 600;
                }
                QStatusBar { background: #edf6fd; color: #47728e; }
                """
            )

    def toggle_theme(self) -> None:
        self.dark = not self.dark
        self.apply_theme()

    def _set_step(self, idx: int) -> None:
        idx = max(0, min(idx, self.pages.count() - 1))
        self.pages.setCurrentIndex(idx)
        for i, btn in enumerate(self.step_buttons):
            btn.setChecked(i == idx)
        self.prev_btn.setEnabled(idx > 0)
        self.next_btn.setEnabled(idx < self.pages.count() - 1)
        self.statusBar().showMessage(self.step_titles[idx])

    def _go_next(self) -> None:
        self._set_step(self.pages.currentIndex() + 1)

    def _go_prev(self) -> None:
        self._set_step(self.pages.currentIndex() - 1)

    def show_help_dialog(self) -> None:
        step = self.pages.currentIndex()
        if step == 1:
            text = (
                "Import Value Help\n\n"
                "- Animal ID: required, unique (example: RAT_001)\n"
                "- Sex: M/F or Male/Female (case-insensitive). Unknown/NA allowed\n"
                "- Weight: numeric > 0 (example: 245.5)\n"
                "- Age: numeric (example: 12)\n"
                "- Cage: text ID (example: C1)\n"
                "- Date of arrival: use calendar, stored as YYYY-MM-DD\n"
                "- Optional fields: Strain, Species, Condition/Notes, Source\n\n"
                "Tip: Use Auto Generate Animal List for fast prefilled rows."
            )
            title = "Help - Animal Import"
        elif step == 2:
            text = (
                "Default/Example Parameters\n\n"
                "- Group Names: Control,Treatment\n"
                "- Method: balanced (recommended default)\n"
                "- Seed: 20260218 (leave empty to auto-generate)\n"
                "- Stratify By: sex,cage,weight\n"
                "- Fixed Block Size: 0 (off)\n"
                "- Random Block Sizes: 4,6,8\n"
                "- Max per Cage per Group: 1\n"
                "- Minimize cage clustering: enabled\n"
                "- Weight balancing: enabled"
            )
            title = "Help - Strategy Configuration"
        else:
            text = (
                "Workflow Help\n\n"
                "1. Create Study\n"
                "2. Import/Add Animals\n"
                "3. Configure Strategy\n"
                "4. Run Randomization\n"
                "5. Review and Export\n\n"
                "Use Previous/Next to navigate steps."
            )
            title = "Help"
        QMessageBox.information(self, title, text)

    def import_animals_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open animal list", "", "Data (*.csv *.xlsx)")
        if not file_path:
            return
        self.animals = import_animals(file_path)
        self._load_animals_into_table(self.animals)
        self.statusBar().showMessage(f"Imported {len(self.animals)} animals from {Path(file_path).name}")

    def add_animal_row(self) -> None:
        row = self.animals_table.rowCount()
        self.animals_table.insertRow(row)
        self._set_combo_cell(row, 1, self.SEX_OPTIONS)
        self._set_combo_cell(row, 6, self.SPECIES_OPTIONS)
        self._set_date_cell(row, 9)

    def _set_combo_cell(self, row: int, col: int, options: list[str], value: str = "") -> None:
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(options)
        if value:
            if combo.findText(value) < 0:
                combo.addItem(value)
            combo.setCurrentText(value)
        self.animals_table.setCellWidget(row, col, combo)

    def _set_text_cell(self, row: int, col: int, value: str = "") -> None:
        self.animals_table.setItem(row, col, QTableWidgetItem(value))

    def _set_date_cell(self, row: int, col: int, value: str = "") -> None:
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setDate(QDate.currentDate())
        date_edit.setToolTip("Select date from calendar or keep today.")
        if value:
            parsed = QDate.fromString(value, "yyyy-MM-dd")
            if not parsed.isValid():
                parsed = QDate.fromString(value, Qt.DateFormat.ISODate)
            if parsed.isValid():
                date_edit.setDate(parsed)
        self.animals_table.setCellWidget(row, col, date_edit)

    def generate_auto_animals(self) -> None:
        count = self.auto_count.value()
        prefix = self.auto_prefix.text().strip() or "ANM"
        start = self.auto_start.value()
        pad = self.auto_pad.value()
        species = self.auto_species.currentText().strip()
        sex_mode = self.auto_sex_mode.currentText()
        strain = self.auto_strain.text().strip()
        source = self.auto_source.text().strip()
        cage = self.auto_cage.text().strip()
        arrival = self.auto_arrival.date().toString("yyyy-MM-dd")

        if self.auto_replace.isChecked() and self.animals_table.rowCount() > 0:
            self.animals_table.setRowCount(0)

        for i in range(count):
            row = self.animals_table.rowCount()
            self.animals_table.insertRow(row)

            animal_number = start + i
            animal_id = f"{prefix}_{animal_number:0{pad}d}"
            if sex_mode == "All Male":
                sex = "M"
            elif sex_mode == "All Female":
                sex = "F"
            elif sex_mode == "Unknown":
                sex = ""
            else:
                sex = "M" if i % 2 == 0 else "F"

            self._set_text_cell(row, 0, animal_id)
            self._set_combo_cell(row, 1, self.SEX_OPTIONS, sex)
            self._set_text_cell(row, 2, "")
            self._set_text_cell(row, 3, "")
            self._set_text_cell(row, 4, cage)
            self._set_text_cell(row, 5, strain)
            self._set_combo_cell(row, 6, self.SPECIES_OPTIONS, species)
            self._set_text_cell(row, 7, "")
            self._set_text_cell(row, 8, source)
            self._set_date_cell(row, 9, arrival)

        self.statusBar().showMessage(
            f"Generated {count} animals. You can edit IDs/species/sex/default values before randomization."
        )

    def _load_animals_into_table(self, animals: list[AnimalRecord]) -> None:
        self.animals_table.setRowCount(0)
        for animal in animals:
            row = self.animals_table.rowCount()
            self.animals_table.insertRow(row)
            values = [
                animal.animal_id,
                animal.sex or "",
                "" if animal.weight is None else str(animal.weight),
                "" if animal.age is None else str(animal.age),
                animal.cage or "",
                animal.strain or "",
                animal.species or "",
                animal.notes or "",
                animal.source or "",
                animal.date_of_arrival or "",
            ]
            for col, value in enumerate(values):
                if col == 1:
                    self._set_combo_cell(row, col, self.SEX_OPTIONS, value)
                elif col == 6:
                    self._set_combo_cell(row, col, self.SPECIES_OPTIONS, value)
                elif col == 9:
                    self._set_date_cell(row, col, value)
                else:
                    self.animals_table.setItem(row, col, QTableWidgetItem(value))

    def _collect_animals_from_table(self) -> list[AnimalRecord]:
        rows: list[AnimalRecord] = []
        for r in range(self.animals_table.rowCount()):

            def _cell(c: int) -> str:
                widget = self.animals_table.cellWidget(r, c)
                if isinstance(widget, QComboBox):
                    return widget.currentText().strip()
                if isinstance(widget, QDateEdit):
                    return widget.date().toString("yyyy-MM-dd")
                item = self.animals_table.item(r, c)
                return "" if item is None else item.text().strip()

            animal_id = _cell(0)
            if not animal_id:
                continue
            weight_text = _cell(2)
            age_text = _cell(3)
            try:
                sex_value = normalize_sex_value(_cell(1) or None)
            except ValueError as exc:
                raise ValueError(f"Invalid sex value at row {r + 1}: {_cell(1)}") from exc
            rows.append(
                AnimalRecord(
                    animal_id=animal_id,
                    sex=sex_value,
                    weight=float(weight_text) if weight_text else None,
                    age=float(age_text) if age_text else None,
                    cage=_cell(4) or None,
                    strain=_cell(5) or None,
                    species=_cell(6) or None,
                    notes=_cell(7) or None,
                    source=_cell(8) or None,
                    date_of_arrival=_cell(9) or None,
                )
            )
        return rows

    def _build_project_from_ui(self) -> ProjectModel:
        animals = self._collect_animals_from_table()
        groups = [x.strip() for x in self.groups.text().split(",") if x.strip()]
        if not groups:
            raise ValueError("At least one group name is required")
        if not animals:
            raise ValueError("At least one animal is required")

        seed_text = self.seed.text().strip()
        stratify = [x.strip() for x in self.stratify_by.text().split(",") if x.strip()]

        try:
            random_blocks = [int(x.strip()) for x in self.random_block_sizes.text().split(",") if x.strip()]
        except ValueError as exc:
            raise ValueError("Random block sizes must be comma-separated integers") from exc

        cfg = RandomizationConfig(
            method=self.method.currentText(),
            group_names=groups,
            seed=int(seed_text) if seed_text else None,
            stratify_by=stratify,
            block_size=self.block_size.value() or None,
            random_block_sizes=random_blocks,
            constraints=ConstraintConfig(
                max_animals_per_cage_per_group=self.max_cage.value() or None,
                minimize_cage_clustering=self.minimize_cage.isChecked(),
                weight_balance=self.weight_balance.isChecked(),
            ),
        )
        meta = StudyMetadata(
            study_id=self.study_id.text().strip(),
            title=self.study_title.text().strip(),
            researcher_name=self.researcher.text().strip(),
            institution=self.institution.text().strip(),
        )
        return ProjectModel(metadata=meta, animals=animals, config=cfg, groups=groups)

    def run_randomization(self) -> None:
        try:
            self.project = self._build_project_from_ui()
            artifacts = RandomizerService().run(self.project)
        except Exception as exc:
            QMessageBox.critical(self, "Randomization failed", str(exc))
            return

        self.run_summary.clear()
        self.run_summary.append(f"Seed: {artifacts.seed}")
        self.run_summary.append(f"Input hash: {artifacts.hashes.get('input_hash')}")
        self.run_summary.append(f"Config hash: {artifacts.hashes.get('config_hash')}")
        self.run_summary.append(f"Output hash: {artifacts.hashes.get('output_hash')}")
        self.run_summary.append("\nWarnings:")
        if artifacts.warnings:
            for warning in artifacts.warnings:
                self.run_summary.append(f"- {warning}")
        else:
            self.run_summary.append("- None")

        self.assignments_table.setRowCount(len(self.project.assignments))
        for i, row in enumerate(self.project.assignments):
            self.assignments_table.setItem(i, 0, QTableWidgetItem(row.animal_id))
            self.assignments_table.setItem(i, 1, QTableWidgetItem(row.group))

        self._set_step(4)
        self.statusBar().showMessage(f"Run complete. Seed={self.project.config.seed}")

    def export_outputs(self) -> None:
        if self.project is None or not self.project.assignments:
            QMessageBox.warning(self, "No results", "Run randomization first")
            return

        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if not folder:
            return

        out_dir = Path(folder)
        export_assignments(self.project.assignments, out_dir / "allocation.csv", animals=self.project.animals)
        bundle = export_interop_bundle(
            self.project.assignments,
            animals=self.project.animals,
            output_dir=out_dir,
            stem="allocation",
        )
        report_path = generate_html_report(self.project, out_dir / "allocation_report.html")
        project_path = out_dir / "study.nprj"
        save_project(self.project, project_path)

        files = [
            ("Allocation CSV", bundle["csv"]),
            ("Allocation XLSX", bundle["xlsx"]),
            ("Allocation TSV", bundle["tsv"]),
            ("Prism Grouped IDs", bundle["prism_grouped"]),
            ("Prism Grouped Weights", bundle["prism_weights_grouped"]),
            ("HTML Report", report_path),
            ("Project Snapshot", project_path),
        ]
        dialog = ExportSummaryDialog(
            parent=self,
            method=self.project.config.method,
            output_dir=out_dir,
            files=files,
        )
        dialog.exec()
        self.statusBar().showMessage("Exported CSV/XLSX/TSV + Prism files + HTML report + project.")


def launch() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
