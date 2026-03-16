# Check Uncited References (CURE)

English | [中文版](./README.zh-CN.md)

**CURE** (Check Uncited REferences) is a streamlined Python tool designed to optimize academic manuscripts by identifying "ghost references"—entries that persist in a bibliography despite being omitted or removed from the main body text during the revision process.

## ❓ Context & Motivation (Use Case)

Contemporary research often necessitates collaboration across heterogeneous document formats. While Zotero and similar ecosystems offer robust synchronization within native Markdown or LaTeX environments, **iterative collaboration in Microsoft Word** frequently destabilizes these citation links.

When Word or PDF drafts are converted back to Markdown for final synthesis or submission, citations are typically rendered as "static text." In the course of intensive revisions, body paragraphs may be deleted while their corresponding entries remain in the reference list. **CURE** addresses this structural vulnerability by employing semantic pattern matching (Semantic Fingerprinting) rather than software-dependent links, ensuring a lean and consistent final manuscript.

## 🔄 Recommended Pipeline

To ensure manuscript integrity, we recommend the following "Legacy-to-Clean" workflow:

### 1. High-Fidelity Conversion
-   **For Word Documents (`.docx`)**: Utilize [Pandoc](https://pandoc.org/) for a robust transition from Word to Markdown.
    ```bash
    pandoc manuscript.docx -o manuscript.md
    ```
-   **For PDF Documents (`.pdf`)**: Standard conversion methods often compromise complex academic layouts. We recommend **[obsidian-marker](https://github.com/l3-n0x/obsidian-marker)**, which leverages **[Mistral AI](https://mistral.ai/)**'s advanced OCR capabilities to extract semantic structures and bibliography entries with high precision.

### 2. Semantic Verification with CURE
Upon generating the `.md` file, execute **CURE** to audit the bibliography and isolate all uncited ghost entries.

## 🚀 Quick Start

### Installation

No installation required. Download `check_uncited.py` and run it via Python 3.

### Basic Usage

Specify your target Markdown file via the command line:

```bash
python3 check_uncited.py -i "your_paper.md"
```

### CLI Options

| Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | **(Required)** Path to the target Markdown file. | N/A |
| `-o` | `--output` | Path for the generated validation report. | `uncited_report.md` |
| `-h` | `--help` | Display the help manual. | N/A |

## 📊 Underlying Mechanism (Heuristic Scoring)

CURE goes beyond simple keyword searching by implementing a **Heuristic Scoring** logic to ensure robust detection:
1.  **Section Identification**: Scans the document for potential bibliography headers across multilingual contexts.
2.  **Density Evaluation**: Scores candidates based on the "entry density" of subsequent lines to accurately identify the bibliography's starting point.
3.  **Fingerprint Extraction**: Isolates the true reference block and extracts unique "Fingerprints" (Author surname + Publication year).
4.  **Cross-Context Matching**: Executes multi-line regex matching throughout the body text to confirm the presence of citations.

## 📝 Deliverables

The tool produces a detailed Markdown report (`uncited_report.md`) listing all references lacking substantive body support, preserving original entries for easy cross-referencing.

## 📖 Technical Documentation

For developers or researchers interested in the underlying heuristics and matching logic, please refer to the **[project_handover.md](./project_handover.md)** file. It provides an in-depth explanation of the heuristic scoring algorithm, fingerprint extraction, and technical implementation details.

## 🤝 Contribution

We welcome forks, issues, and pull requests to further refine the detection algorithms and support additional citation formats.
