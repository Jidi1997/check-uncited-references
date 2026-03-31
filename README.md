# Check Uncited References (CURE)

English | [中文版](./README.zh-CN.md)

**CURE** (Check Uncited REferences) is a streamlined Python tool specifically designed for **Markdown** documents. Given that Markdown provides an inherently structured and AI-friendly format, CURE leverages this clarity to identify "ghost references"—entries that persist in a bibliography despite being omitted or removed from the main body text.

---

### 🌟 Latest Updates (March 2026 - v3.0)

Version 3.0 introduces significant accuracy and stability improvements:
- **Unicode-Aware Matching**: Precise identification of author names in multilingual (English/Chinese) environments.
- **Improved Bibliography Parsing**: Automatic detection of bibliography boundaries to prevent false positives from appendicies or TOCs.
- **Robustness**: Heuristic-based publication year extraction for dense-packed reference lists.
- **Legacy Support**: The stable v2.x version is now preserved in the `legacy/` directory.

For a detailed technical breakdown, see the **[OPTIMIZATION_LOG.md](./OPTIMIZATION_LOG.md)**.

---

## ❓ Context & Motivation (Use Case)

In modern research, writing often moves between different formats. While tools like Zotero excel at managing citations within Markdown or $\LaTeX$ , the back-and-forth of **collaborative editing in Microsoft Word** can easily break these links.

Then, citations in Word often become “static text.” During revisions, you might delete a paragraph but forget to remove its now‑orphaned reference, leaving ghost entries in your bibliography.
**CURE** solves this. Instead of relying on fragile, app-specific links, it identifies references by their core semantic content, helping you automatically find and remove these redundant citations for a clean, consistent manuscript.


## 🔄 Recommended Pipeline

To ensure manuscript integrity, we recommend the following "Legacy-to-Clean" workflow:

### 1. High-Fidelity Conversion
-   **For Word Documents (`.docx`)**: Utilize [Pandoc](https://pandoc.org/) for a robust transition from Word to Markdown.
    ```bash
    pandoc manuscript.docx -o manuscript.md
    ```
-   **For PDF Documents (`.pdf`)**: Standard conversion methods often compromise complex academic layouts. We recommend **[obsidian-marker](https://github.com/l3-n0x/obsidian-marker)**, which leverages **[Mistral AI](https://mistral.ai/)**'s advanced OCR capabilities to extract semantic structures and bibliography entries with high precision.

### 2. Semantic Verification with CURE
Upon generating the `manuscript.md` file, execute **CURE** to audit the bibliography:

## 🚀 Quick Start

### Installation

No installation required. Download `check_uncited.py` and run it via Python 3.

### Basic Usage

Specify your target Markdown file via the command line:

```bash
python3 check_uncited.py -i "manuscript.md"
```

### CLI Options

| Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | **(Required)** Path to the target Markdown file. | N/A |
| `-o` | `--output` | Path for the generated validation report. | `uncited_report.md` |
| `-h` | `--help` | Display the help manual. | N/A |

## 📊 Underlying Mechanism (Smart Scoring System)

CURE moves beyond basic text search by using a **Smart Scoring** mechanism for accurate detection:
1.  **Section Identification**: Automatically scans the document to find potential bibliography headers.
2.  **Content Analysis**: Evaluates the formatting density of subsequent lines to pinpoint the exact start of the reference list.
3.  **Feature Extraction**: Once the references are located, it extracts unique identifiers (Author surname + Publication year) for each entry.
4.  **Contextual Verification**: Performs advanced multi-line matching within the body text to confirm if a reference is genuinely cited.

## 📝 Deliverables

The tool produces a detailed Markdown report (`uncited_report.md`) listing all references lacking substantive body support, preserving original entries for easy cross-referencing.

## 📖 Technical Documentation

For developers or researchers interested in the underlying heuristics and matching logic, please refer to the **[project_handover.md](./project_handover.md)** file. It provides an in-depth explanation of the heuristic scoring algorithm, fingerprint extraction, and technical implementation details.

## 🤝 Contribution

We welcome forks, issues, and pull requests to further refine the detection algorithms and support additional citation formats.
