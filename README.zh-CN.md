# CURE (学术引用校验工具)

[English](./README.md) | 中文版

**CURE** (Check Uncited REferences) 是一款专为 **Markdown** 文档内核设计的轻量级 Python 脚本。由于 Markdown 文本具有高度的结构化特征，极易与各类 AI 工具产生深度联动，本工具旨在通过精准识别文末参考文献列表中的“冗余文献”/“幽灵文献”（即在正文论述中未被提及的文献条目），保障学术文档的严谨性。

## ❓ 应用背景

在科研学术写作中，多种文档格式之间的协作与转换已是常态。尽管借助 Better BibTeX，Zotero 在原生 Markdown 与 $/LaTeX$  环境中的引用管理表现优异，但在**跨平台的 Microsoft Word 复审与迭代**流程中，引用链接却很容易发生断裂。

当 Word 或 PDF 初稿被重新转换为 Markdown 进行汇总或提交时，其引用关系往往会退化为“静态文本”。在繁复的修订过程中，作者常会删除特定的正文内容，却极易遗漏文末相应的参考文献条目。**CURE** 旨在通过“语义级指纹提取”（Semantic Fingerprinting）而非脆弱的软件内部连接，协助作者有效清理此类转换过程中产生的冗余文献/幽灵文献。

## 🔄 典型应用方案

为确保最终交付文档的简洁性与严谨性，建议采用以下流程：

### 1. 结构化转换
-   **Word 稿件 (`.docx`)**：建议使用 [Pandoc](https://pandoc.org/) 实现从 Word 到 Markdown 的结构化转换。
    ```bash
    pandoc manuscript.docx -o manuscript.md
    ```
-   **PDF 稿件 (`.pdf`)**：考虑到复杂学术排版的特殊性，推荐采用基于 **[Mistral AI](https://mistral.ai/)** 高级 OCR 模型的 **[obsidian-marker](https://github.com/l3-n0x/obsidian-marker)**。该方案能够精准识别文档层级，最大程度保留文献条目的语义完整性。

### 2. 智能化语义校验
在获得 `manuscript.md` 文件后，通过 **CURE** 运行自动化脚本：

## 🚀 快速使用

### 环境要求

无需额外安装流程。仅需下载 `check_uncited.py` 并在 Python 3 终端环境下运行。

### 执行命令

使用命令行指定待分析的 Markdown 路径：

```bash
python3 check_uncited.py -i "manuscript.md"
```

### 可选参数

| 缩写 | 全称 | 功能描述 | 默认值 |
| :--- | :--- | :--- | :--- |
| `-i` | `--input` | **(必选)** 待处理的 Markdown 文件路径 | N/A |
| `-o` | `--output` | 校验报告导出路径 | `uncited_report.md` |
| `-h` | `--help` | 调取帮助文档 | N/A |

## 📊 核心识别机制 (Heuristic Scoring)

CURE 并非基于简单的关键词轮询，而是通过**启发式评分机制**来保障识别的稳健性：
1.  **分块识别**：全局扫描潜在的参考文献声明头。
2.  **密度分析**：通过探测候选区后续行的“条目特征密度”来对潜在起始位点进行加权评分。
3.  **指纹提取**：精准定位真实的文献区块，并提取由“作者姓氏 + 出版年份”构成的检索指纹。
4.  **交叉核验**：在正文语境中执行跨行正则匹配，最终判定该条目是否被实质性引用。

## 📝 结果交付

程序将导出详细的 Markdown 报告 (`uncited_report.md`)，清晰罗列出所有缺乏正文支撑的文献条目，并保留原文信息供作者复核。

## 📖 技术移交与开发文档

如果您希望深入了解本工具的底层逻辑或对其进行二次开发，请参考 **[project_handover.md](./project_handover.md)**。该文档详细记录了启发式评分算法、指纹提取逻辑及跨行模糊匹配的技术实现。

## 🤝 协作与贡献

欢迎通过 Fork、Issue 或 Pull Request 等方式参与项目维护，共同优化文献识别算法。
