# Check Uncited References (CURE)

English | [中文版](./README.zh-CN.md)

**CURE** is a lightweight Python tool designed for researchers and PhD students to automatically detect "ghost references"—entries listed in your bibliography that are never actually cited in the main body of your document.

## 🌟 Features

-   **Dual-Language Support**: Works seamlessly with both English and Chinese academic documents.
-   **Intelligent Splitting**: Uses a heuristic scoring algorithm to accurately separate the main text from the bibliography, even if "References" appears in the Table of Contents.
-   **Universal Parsing**: Supports both numbered bibliography (e.g., `[1]`, `1.`) and unnumbered APA-style lists (e.g., `Aghion, P. (2013)`).
-   **Fuzzy Matching**: Detects citations even if they are split across multiple lines or use various shorthand formats (e.g., `Author et al., 2020`).
-   **Zero Dependencies**: Written in pure Python 3 using only standard libraries.

## 🚀 Quick Start

### Installation

No installation required. Just download `check_uncited.py` and you are good to go.

### Usage

Run the tool from your terminal by specifying your input Markdown file:

```bash
python3 check_uncited.py -i "your_thesis_draft.md"
```

### Options

| Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | **(Required)** Path to your input Markdown file. | N/A |
| `-o` | `--output` | Path to save the uncited references report. | `uncited_report.md` |
| `-h` | `--help` | Show the help message and exit. | N/A |

## 📊 How It Works

CURE doesn't just look for keywords. It uses a **Heuristic Scoring** approach:
1.  It scans the document for potential bibliography headers.
2.  It evaluates each candidate by checking the **density** of reference-like patterns in the following lines.
3.  It selects the true bibliography section and extracts "Fingerprints" (Author surnames + Year).
4.  It performs a cross-line regex search in the body text to verify each fingerprint.

## 📝 Output

The tool generates a Markdown report (`uncited_report.md`) listing every reference that lacks a corresponding citation in the body, complete with original text for easy identification.

## 🤝 Contributing

Feel free to fork this project, report bugs, or submit pull requests to help improve the detection logic!
