# 🎓 Agentic-Class-Assistant：助教改卷与统分 Skill

- **网页直达（含附件/截图）**：https://yurucamp.notion.site/4228de2e6f7d8130a13cdf15485862bc
- **分类**：教学与助教
- **标签**：AI Skill, 助教
- **所属页面**：YE Group Toolkit
- **Notion 最后更新**：2026-11-25T07:12:00.000Z

---

> 🎓 **Agentic-Class-Assistant：助教改卷与统分 Skill**
> 面向教师与助教的全中文交互式 Gemini / Antigravity Skill，通过命令行辅助自动化管理班级作业：下载作业包、利用大模型多模态能力直接批改原始 PDF/DOCX 作业、计算本地 Excel/CSV 成绩单统计数据，并支持同步成绩至课堂派（Mock）。


- 🔗 [https://github.com/Misaka16384/Agentic-Class-Assistant](https://github.com/Misaka16384/Agentic-Class-Assistant)


## ✨ 核心功能

1. **全中文交互与人工确认**：
  - 交互向导逐步确认关键参数（评分细则比重、目标文件、课堂会话 ID）。
  - 需要人工介入的操作（如从邮箱下载附件）提供清晰中文指引；向本地文件写入成绩或同步云端前强制要求人工确认。
2. **多模态直接批改作业**：
  - 支持直接读取学生提交的原始 **PDF** 与 **DOCX** 文件，对照预设 JSON 评分标准（`rubric.json`）逐项打分。
3. **自动成绩统计与报告生成**：
  - 自动更新 Excel / CSV 成绩单，计算平均分、中位数与各分数段人数分布，生成格式化的中文统计报告。
4. **完整自动化测试保障**：
  - 内置单元测试与覆盖 Tier 1–4 的端到端测试套件（共 112 个 `pytest` 测试用例），保障评分与统分流程稳定可靠。

## 📂 项目结构

- `SKILL.md` — Gemini / Antigravity Skill 配置文件
- `bin/class_assistant.py` — 主交互式中文 CLI 工具
- `src/grading.py` — 作业文档解析与多模态评分模块
- `src/spreadsheet.py` — 成绩单电子表格管理与统计模块
- `src/syncing.py` — 课堂派同步与下载（Mock）模块
- `tests/` 与 `tests_e2e/` — 单元测试及 Tier 1–4 端到端测试套件

## 🚀 快速使用


```bash
# 克隆仓库
git clone https://github.com/Misaka16384/Agentic-Class-Assistant.git
cd Agentic-Class-Assistant

# 1. 交互模式：启动中文命令行批改与统分向导
python bin/class_assistant.py \
  --class-id "physics_101" \
  --rubric "rubric.json" \
  --grades-file "grades.csv" \
  --output-dir "submissions"

# 2. 非交互式 Dry-run 空转测试模式
python bin/class_assistant.py --dry-run

# 3. 运行全部 112 个自动化测试
pytest
```
