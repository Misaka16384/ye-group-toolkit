# 🌌 审稿回复模板（Reply）

- **网页直达（含附件/截图）**：https://yurucamp.notion.site/997d67e1fe8c4a4a92e1d692c6196c93
- **分类**：写作与排版
- **标签**：LaTeX, Overleaf
- **所属页面**：YE Group Toolkit
- **可直下附件**：`reply.tex`, `latexmkrc.txt`, `reply.pdf`（`python query.py download reply-997d67e1`）
- **Notion 最后更新**：2026-11-25T07:11:00.000Z

---

> 🌌 **审稿意见回复信 LaTeX 模板**
> 基于 `tcolorbox` 的分栏式审稿回复模板，清晰区分审稿意见与作者回复，支持跨页、Overleaf 编译及章节交叉引用。


## 📦 模板文件


- 📎 **可直下附件**：`reply.tex`（约 32 KB）— 可用命令 `python query.py download reply-997d67e1 reply.tex` 直接下载到本地


- 📎 **可直下附件**：`latexmkrc.txt`（约 4 KB）— 可用命令 `python query.py download reply-997d67e1 latexmkrc.txt` 直接下载到本地


- 📎 **可直下附件**：`reply.pdf`（约 171 KB）— 可用命令 `python query.py download reply-997d67e1 reply.pdf` 直接下载到本地


## 📖 使用说明

1. 基本的文本框样式：

```latex
\begin{tcolorbox}{title = yourtitle, breakable, colframe=blue} 
\textbf{Referee: }XXXXXXXX
\tcblower
\textbf{Reply: }XXXXXXXX
\end{tcolorbox}
```

在以上代码中，$\mathtt{title=yourtitle}$选项让你指定文本框的标题，$\mathtt{breakable}$选项允许你的文本框跨页，$\mathtt{colframe=blue}$选项让你的文本框具有蓝色外观。$\mathtt{\backslash tcblower}$命令用于创建一条分割线。

示例效果：


> 🖼️ *（原页包含示例截图，请打开本页对应的 Notion 网页链接查看）*

1. 在overleaf中，为reply添加指向文章中章节的交叉引用：

- 🔗 [https://www.overleaf.com/learn/how-to/Cross_referencing_with_the_xr_package_in_Overleaf](https://www.overleaf.com/learn/how-to/Cross_referencing_with_the_xr_package_in_Overleaf)
