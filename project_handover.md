# CURE (Check Uncited References) - Technical Handover Documentation

## 🗒️ Overview
This tool is designed to automate the cross-referencing between the "body text" and the "bibliography section" of a Markdown document. It identifies "ghost references"—entries listed in the bibliography that are never cited in the main text.

### Problem Statement: Post-Conversion Artifacts
In contrast to LaTeX or Zotero-native Markdown workflows where citations are live-linked, collaboration in **Microsoft Word** often results in "static" citations. When converting these legacy documents via tools like **Pandoc**, reference links are lost. During iterative editing, text is often deleted without updating the bibliography. CURE uses semantic fingerprinting (Author + Year) to find these abandoned entries where traditional bibliographic software fails.

## 🛠️ Core Engineering Logic

### 1. Heuristic Bibliography Splitting
To prevent false positives from keywords appearing in the Table of Contents or body discussions, the script uses a **Heuristic Scoring Algorithm**:
- **Candidate Scanning**: Locates all occurrences of keywords like `References`, `Bibliography`, or `参考文献`.
- **Structure Density Validation**: For each candidate, the script "previews" the next 20 lines.
- **Scoring**: Points are awarded if lines match standard bibliographic patterns (e.g., `[1]` or `Surname, Year`).
- **Final Split**: The candidate with the highest score is chosen as the true start of the bibliography, ensuring the body text search area is clean.

### 2. Universal Reference Parsing
The parser is built to be language-agnostic and supports:
- **Numbered Formats**: `[1] Author, Year...` or `1. Author, Year...`
- **Author-Date (APA/MLA) Styles**: `Aghion, P., & Jones, B. (2013). ...`
- **Fingerprinting**: It automatically extracts the primary author surnames and the publication year to create a search "fingerprint" for each entry.

### 3. Cross-Line Fuzzy Matching
- **DOTALL Regex**: Uses the `re.DOTALL` flag to find citations even if the author and year are separated by a newline in the source text.
- **Citation Variations**: Supports multiple citation styles in the body, such as `(Author et al., 2020)`, `(Author A & Author B, 2020)`, or `Author (2020) suggests...`.

## 🚀 Deployment & Usage

### Requirements
- **Python 3.x**
- No 3rd-party dependencies (Pure Python).

### CLI Usage
```bash
# Basic usage (default output to uncited_report.md)
python3 check_uncited.py -i "your_document.md"

# Specify custom output path
python3 check_uncited.py -i "input.md" -o "custom_report.md"
```

## ⚠️ Maintenance Guide
For future updates, focus on these functions:
- `is_line_reference_like()`: Modify this to support new or unconventional bibliography styles.
- `parse_reference()`: Adjust author splitting logic if dealing with non-standard name formats.
- `find_bibliography_split()`: Fine-tune the scoring threshold if a specific document structure causes splitting issues.
