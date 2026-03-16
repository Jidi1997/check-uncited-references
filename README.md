# Check Uncited References (CURE)

English | [中文版](./README.zh-CN.md)

**CURE** is a lightweight Python tool designed for researchers and PhD students to automatically detect "ghost references"—entries listed in your bibliography that are never actually cited in the main body of your document.

## ❓ The "Why" (Use Case)

In modern research, we often collaborate across different formats. While Zotero-native Markdown or LaTeX workflows maintain perfect synchronization, **collaborating in Microsoft Word** often breaks citation links during multiple iterations of manual editing and format conversion. 

When converting Word or PDF drafts back to Markdown for final assembly or submission, citations become "static text," making it easy to accidentally delete a paragraph while leaving its corresponding bibliography entry behind. **CURE** is specifically built to solve this "conversion-artifact" problem by using semantic pattern matching instead of live software links.

## 🔄 Recommended Workflow

For the best results, we recommend a "Source to Clean" workflow based on your input format:

### 1. Format Conversion
-   **For Word (`.docx`)**: Use [Pandoc](https://pandoc.org/) to convert into Markdown.
    ```bash
    pandoc your_paper.docx -o your_paper.md
    ```
-   **For PDF (`.pdf`)**: Using standard conversion often yields poor results for complex academic layouts. We recommend using high-quality OCR tools like **[obsidian-marker](https://github.com/l3-n0x/obsidian-marker)**, which leverages **[Mistral AI](https://mistral.ai/)**'s powerful OCR capabilities to preserve structural integrity during the PDF-to-Markdown process.

### 2. Clean Up with CURE
Once you have your `.md` file, run **CURE** to identify and remove all uncited ghost references.

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
