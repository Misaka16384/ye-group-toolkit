# YE Group Toolkit（叶鹏课题组工具箱 Skill）

中山大学物理学院 [叶鹏课题组（凝聚态理论）](https://yepengcmt.github.io/yepcmt/) 官方工具箱的动态知识库与一键安装 Agent Skill。

- **人类网页版（推荐日常浏览与下载模板附件）**：https://yurucamp.notion.site/ye-group-toolkit
- **AI 知识库（自动从 Notion 同步为纯 Markdown）**：[`kb/index.md`](kb/index.md)
- **维护人**：[Jie-Yu Zhang](https://github.com/Misaka16384)

---

## 一键安装到你的 AI Agent

支持 **Antigravity、Claude Code、Codex、Gemini CLI、Cursor、OpenCode、GitHub Copilot、Qwen Code** 等所有兼容 [Agent Skills](https://agentskills.io/) 的工具。

### 方式一：一行命令全局安装（推荐）

```bash
npx skills add Misaka16384/ye-group-toolkit --skill ye-group-toolkit -g
```

> 若只想在当前项目安装，去掉 `-g` 即可。

### 方式二：直接发一句话给你的 AI 助手

直接复制下面这句话发给你的本地 AI 助手：

> 请阅读 `https://github.com/Misaka16384/ye-group-toolkit` 并按 README 帮我全局安装 `ye-group-toolkit` skill。

---

## 安装后怎么用？

装好后无需任何配置、无需浏览器、无需 Notion 账号或 API Key。直接问你的 AI 即可：

- “中大差旅费怎么走线上电子网审报销？需要哪些附件？”
- “怎么给组里学生发劳务费？每月几号截止？”
- “组里服务器怎么 SSH 连接？找谁要密码？”
- “办公室华为打印机在 Mac / iPhone 上怎么连？”
- “帮我把组里的 RevTeX 科研笔记模板（或审稿回复/中大海报模板）直接下载到当前文件夹！”

每次查询时，Skill 会自动从本仓库的 `kb/` 拉取**最新同步的 Markdown 内容与模板附件（`.zip` / `.tex` / `.pdf` 等 ≤ 25 MB 的文件会自动镜像到 `kb/assets/`）**（优先 GitHub Raw，校园网/国内自动回退 jsDelivr CDN），并在需要查看截图或大文件时附上 Notion 网页直达链接。

---

## 动态同步机制（维护者说明）

本仓库通过 [`.github/workflows/sync-notion.yml`](.github/workflows/sync-notion.yml) 与 [`scripts/sync_notion.py`](scripts/sync_notion.py) 调用 Notion 官方只读 API，**每日定时自动同步**（也支持在 GitHub Actions 页面一键手动触发）`YE Group Toolkit` 的全部页面、数据库条目及嵌套子页到 `kb/` 目录：

1. 维护者只需在 Notion 里正常编辑内容；
2. GitHub Actions 自动将最新内容导出为纯 Markdown 并提交到 `main`；
3. 课题组同学的 AI Agent 每次查询实时读取远端最新 `kb/`，**无需重新安装或更新 Skill**。

### 配置 Secrets（仅维护者一次性操作）
- 在仓库 `Settings -> Secrets and variables -> Actions` 添加：
  - `NOTION_TOKEN`：已授权连接 `YE Group Toolkit` 页面的 Notion 只读 Internal Integration Secret。
