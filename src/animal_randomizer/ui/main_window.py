from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..io_handlers import export_assignments, import_animals
from ..models import AnimalRecord, ConstraintConfig, ProjectModel, RandomizationConfig, StudyMetadata
from ..project_io import save_project
from ..report import generate_html_report
from ..service import RandomizerService


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Neuroprocessing Randomizer")
        self.resize(1280, 780)

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

        root = QWidget()
        root_layout = QHBoxLayout(root)

        self.sidebar = self._build_sidebar()
        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_study_page())
        self.pages.addWidget(self._build_animals_page())
        self.pages.addWidget(self._build_config_page())
        self.pages.addWidget(self._build_run_page())
        self.pages.addWidget(self._build_results_page())

        right = QVBoxLayout()
        right.addWidget(self.pages)

        nav = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.theme_btn = QPushButton("Toggle Theme")
        self.prev_btn.clicked.connect(self._go_prev)
        self.next_btn.clicked.connect(self._go_next)
        self.theme_btn.clicked.connect(self.toggle_theme)
        nav.addWidget(self.theme_btn)
        nav.addStretch()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.next_btn)
        right.addLayout(nav)

        root_layout.addWidget(self.sidebar, 1)
        wrapper = QWidget()
        wrapper.setLayout(right)
        root_layout.addWidget(wrapper, 4)

        self.setCentralWidget(root)
        self.statusBar().showMessage("Ready")

        self.apply_theme()
        self._set_step(0)

    def _build_sidebar(self) -> QWidget:
        card = QWidget()
        layout = QVBoxLayout(card)
        self.step_buttons: list[QPushButton] = []
        title = QLabel("Neuroprocessing Randomizer")
        subtitle = QLabel("Reproducible Animal Group Allocation")
        title.setObjectName("navTitle")
        subtitle.setObjectName("navSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        for idx, name in enumerate(self.step_titles):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked=False, i=idx: self._set_step(i))
            self.step_buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch()
        return card

    def _build_study_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Create Study"))

        form = QFormLayout()
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Import or Add Animals"))

        buttons = QHBoxLayout()
        self.import_btn = QPushButton("Import CSV/XLSX")
        self.add_row_btn = QPushButton("Add Animal Row")
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Define Groups and Strategy"))

        grid = QGridLayout()
        self.groups = QLineEdit("Control,Treatment")
        self.method = QComboBox()
        self.method.addItems(["simple", "balanced", "stratified", "block"])
        self.seed = QLineEdit("")
        self.stratify_by = QLineEdit("sex,cage,weight")
        self.block_size = QSpinBox()
        self.block_size.setRange(0, 500)
        self.block_size.setValue(0)
        self.random_block_sizes = QLineEdit("4,6,8")
        self.max_cage = QSpinBox()
        self.max_cage.setRange(0, 20)
        self.max_cage.setValue(1)
        self.minimize_cage = QCheckBox("Minimize cage clustering")
        self.minimize_cage.setChecked(True)
        self.weight_balance = QCheckBox("Enable weight balancing")
        self.weight_balance.setChecked(True)

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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Run Randomization"))

        self.run_btn = QPushButton("Run Now")
        self.run_btn.clicked.connect(self.run_randomization)
        layout.addWidget(self.run_btn)

        self.run_summary = QTextEdit()
        self.run_summary.setReadOnly(True)
        layout.addWidget(self.run_summary)
        return page

    def _build_results_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Review Results and Export"))

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
                QWidget { background: #081326; color: #e7f8ff; font-size: 13px; }
                #navTitle { font-size: 18px; font-weight: 700; color: #5ad8ff; }
                #navSubtitle { color: #99dff5; }
                QLineEdit, QComboBox, QSpinBox, QTableWidget, QTextEdit {
                    background: #0f1f38; border: 1px solid #29527b; border-radius: 6px;
                }
                QPushButton {
                    background: #11b8de; color: #021422; border: 0; border-radius: 8px; padding: 8px 10px; font-weight: 700;
                }
                QPushButton:checked { background: #5ad8ff; }
                """
            )
        else:
            self.setStyleSheet(
                """
                QWidget { background: #f4f9ff; color: #12314f; font-size: 13px; }
                #navTitle { font-size: 18px; font-weight: 700; color: #006f8e; }
                #navSubtitle { color: #40718a; }
                QLineEdit, QComboBox, QSpinBox, QTableWidget, QTextEdit {
                    background: #ffffff; border: 1px solid #adc9dc; border-radius: 6px;
                }
                QPushButton {
                    background: #0d8fb2; color: #ffffff; border: 0; border-radius: 8px; padding: 8px 10px; font-weight: 700;
                }
                QPushButton:checked { background: #0bb4df; }
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
                self.animals_table.setItem(row, col, QTableWidgetItem(value))

    def _collect_animals_from_table(self) -> list[AnimalRecord]:
        rows: list[AnimalRecord] = []
        for r in range(self.animals_table.rowCount()):
            def _cell(c: int) -> str:
                item = self.animals_table.item(r, c)
                return "" if item is None else item.text().strip()

            animal_id = _cell(0)
            if not animal_id:
                continue
            weight_text = _cell(2)
            age_text = _cell(3)
            rows.append(
                AnimalRecord(
                    animal_id=animal_id,
                    sex=_cell(1) or None,
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

        seed_text = self.seed.text().strip()
        stratify = [x.strip() for x in self.stratify_by.text().split(",") if x.strip()]
        random_blocks = [int(x.strip()) for x in self.random_block_sizes.text().split(",") if x.strip()]

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
        export_assignments(self.project.assignments, out_dir / "allocation.csv")
        generate_html_report(self.project, out_dir / "allocation_report.html")
        save_project(self.project, out_dir / "study.nprj")

        QMessageBox.information(self, "Export complete", f"Saved outputs to {out_dir}")
        self.statusBar().showMessage("Exported allocation.csv, allocation_report.html, study.nprj")


def launch() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
