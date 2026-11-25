# 🎬 Motif：3B1B 风格学术报告 PPT Skill

- **网页直达（含附件/截图）**：https://yurucamp.notion.site/4228de2e6f7d813298d7fe71e4a3b8e8
- **分类**：展示与海报
- **标签**：AI Skill, Manim
- **所属页面**：YE Group Toolkit
- **Notion 最后更新**：2026-11-25T07:12:00.000Z

---

> 🎬 **Motif：3B1B 风格学术报告 PPT Skill**
> 面向科研人员的轻量级 Agent Skill：围绕一个核心问题组织报告叙事，通过解释性 Manim 动画让公式与物理图像保持对应，并导出经过校验的 HTML / PPTX 演示文稿。


- 🔗 [https://github.com/Misaka16384/motif](https://github.com/Misaka16384/motif)


## ✨ 核心特点

- **叙事驱动的 5 阶段协作流程**：
  1. **锚定核心问题**：先阅读论文与背景材料，提炼整场报告要回答的唯一核心问题。
  2. **先做关键机制动画样片**：在全面铺开前先验证视觉语言、符号对应关系与讲解节奏。
  3. **自动渲染与诊断校验**：按统一场景列表顺序渲染，自动检测画面尺寸、帧率节奏、裁切与图文重叠。
  4. **作者复盘迭代**：将反馈提炼为全局原则并应用到整套幻灯片。
  5. **版本化交付导出**：支持离线交互式 **HTML** 与内嵌 H.264 视频的 **PPTX**（翻页自动播放）。
- **渲染规范与断点续作**：
  - 默认深色学术语义配色，支持 720p30 快速预览与 **2560 × 1440 @ 60 fps** 终版渲染。
  - 通过 `PROJECT.md` 持续记录状态与下一步，支持不同会话/代理无缝接力（配套 `status` / `check` 命令）。
  - *PPTX 自动播放提示*：上台前建议在实际演示电脑的 PowerPoint / WPS 中实测翻页自动播放效果。
- **动画示例**：可在 [GitHub Releases](https://github.com/Misaka16384/motif/releases) 观看 1440p60 演示片段（含元胞自动机对称性图案、公式与晶格对象对应、子系统电荷守恒与任意子迁移率约束等）。

## 📦 安装方式


### 方式一：让本地 AI 助手自动安装

直接向你的本地 AI 助手发送：


```text
请阅读 https://github.com/Misaka16384/motif 并按照 README 帮我安装 Motif。
```


### 方式二：命令行安装（`npx skills`）


```bash
# 项目级安装（默认）
npx skills add Misaka16384/motif --skill motif

# 全局安装（将 AGENT_ID 替换为对应宿主的标识）
npx skills add Misaka16384/motif --skill motif -a AGENT_ID -g -y
```

- 常见 `--agent` 标识包括 `codex`、`claude-code`、`gemini-cli`、`opencode`、`qwen-code`、`github-copilot`、`cursor`；也可从 [Releases](https://github.com/Misaka16384/motif/releases) 手动下载独立 Skill ZIP 解压到对应目录。
- **渲染环境（与 Skill 安装分离）**：Python 3.10+，已验证基线为 `Manim 0.19.1` + `Manim Slides 5.7.0` + LaTeX / `dvisvgm`（Windows 与 Linux 已通过 CI 验证）。

## 🚀 快速开始

新建学术报告项目时，可直接向 AI 助手描述论文、时长与听众背景并调用 `motif`：


```text
使用 motif 根据这些论文准备一份 40 分钟的学术报告，听众包含本方向以外的同行。先和我讨论核心问题与叙事主线；等我们确认一个核心机制动画样片后，再自主完成初稿并复核。
```

继续已有项目：


```text
使用 motif 查找我现有的报告项目并展示当前进度，从记录的下一步继续推进。
```
