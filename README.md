# Animal Randomizer 🐀🎲  
**Reproducible random group assignment for animal studies (rodent neuroscience workflows).**

Animal Randomizer is a lightweight open-source tool developed by **Neuroprocessing** for generating
reproducible, transparent, and publication-ready randomization tables for animal experiments.

This tool is designed for neuroscience rodent studies (rats/mice), but can be used in any biomedical
or experimental research requiring randomized group allocation.

---

## Why this tool?

Randomization is one of the most critical steps in experimental design. Poor or undocumented group allocation
can introduce bias and compromise reproducibility.

Animal Randomizer provides:

- ✅ Seed-based reproducibility (same seed → same randomization table)
- ✅ Publication-ready outputs (CSV/Excel-ready)
- ✅ Simple CLI workflow for lab usage
- ✅ Transparent, auditable randomization logs
- ✅ Extensible architecture (block / stratified randomization roadmap)

---

## Features (v0.1.0)

- Simple random allocation
- Balanced distribution across groups
- Optional custom group names
- CSV export
- Reproducible output with random seed

---

## Installation

### Option 1: Clone from GitHub
```bash
git clone https://github.com/neuroprocessing/animal-randomizer.git
cd animal-randomizer
pip install -r requirements.txt
```

### Option 2: Install as editable package (recommended for development)
```bash
pip install -e .
```

---

## Quick Start

### Example: Randomize 24 animals into 2 groups
```bash
python -m animal_randomizer.cli --n 24 --groups 2 --seed 42 --out output.csv
```

This generates a CSV file like:

| Animal_ID | Group |
|----------|-------|
| RAT_001  | Group A |
| RAT_002  | Group B |
| ...      | ... |

---

## CLI Options

| Argument | Description |
|---------|-------------|
| `--n` | Number of animals |
| `--groups` | Number of groups |
| `--seed` | Random seed for reproducibility |
| `--out` | Output CSV file path |
| `--names` | Optional group names (comma-separated) |

Example with custom group names:

```bash
python -m animal_randomizer.cli --n 30 --groups 3 --names Control,DrugA,DrugB --seed 123 --out study.csv
```

---

## Output Format

The generated CSV contains:

- `Animal_ID`
- `Group`
- `Randomization_Seed`
- `Method`
- `Timestamp`

This output format is designed to be directly included in supplementary materials of scientific papers.

---

## Scientific Use Case

Typical workflow:

1. Define study sample size (N)
2. Choose group structure (Control vs Treatment)
3. Generate randomization table
4. Assign animal cage IDs to group IDs
5. Export and store allocation file in your experiment log folder
6. Cite the tool in your manuscript for reproducibility

---

## Roadmap

Planned upcoming releases:

- Block randomization
- Stratified randomization (weight, age, baseline sucrose preference)
- Excel export
- PDF summary report
- GUI (PyQt6) for lab technicians
- Integration into a larger animal study management suite

---

## Contributing

We welcome contributions from researchers, engineers, and neuroscience labs.

To contribute:

1. Fork the repository
2. Create a new branch (`feature/my-feature`)
3. Commit changes
4. Open a Pull Request

---

## Citation

If you use this software in your research, please cite it.

GitHub will automatically generate citation formats using the included `CITATION.cff`.

---

## License

This project is released under the **MIT License**.

---

## Maintainers

Developed by **Neuroprocessing**  
Open Neuroscience Systems Lab

- Ali Mirzakhani (Founder, Neuroengineering & AI)  
- Neuroprocessing Team Contributors

Repository: https://github.com/neuroprocessing/animal-randomizer

---

## Contact

For collaboration, grants, and open science partnerships:

📧 neuroprocessing@gmail.com
🌍 https://github.com/neuroprocessing
