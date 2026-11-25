---
name: ye-group-toolkit
description: >-
  查询中山大学物理学院叶鹏课题组（YE Group）官方工具箱最新内容：包括中大差旅报销（线上电子网审与线下投单）、
  劳务费发放（薪酬门户）、课题组服务器与天河星逸超算资源、办公室华为打印机与打印店预付款、
  LaTeX 模板（科研笔记/审稿回复/中大海报）及组内自研 Agent Skills。
  当用户询问叶鹏课题组或中山大学相关的报销、发劳务费、服务器、打印机、模板或组内资源时激活此技能。
---

# YE Group Toolkit（叶鹏课题组工具箱）

本技能让 AI 无需浏览器、无需 Notion 账号，直接动态查询叶鹏课题组工具箱的最新内容（自动同步自官方 Notion 公开页 [https://yurucamp.notion.site/ye-group-toolkit](https://yurucamp.notion.site/ye-group-toolkit)）。

## 查询方式（务必实时拉取，不要靠记忆猜测）

使用本技能自带的零依赖脚本 `scripts/query.py`（仅用 Python 3 标准库，自动优先读取 GitHub 最新版并在国内/校园网环境下自动回退 jsDelivr CDN）：

1. **查看全站目录与所有页面标识（slug）**：
   ```bash
   python "<skill-dir>/scripts/query.py" list
   ```
2. **按关键词检索条目与正文**：
   ```bash
   python "<skill-dir>/scripts/query.py" search 报销
   python "<skill-dir>/scripts/query.py" search 打印机 --full
   ```
3. **读取指定页面的完整最新 Markdown 攻略**：
   ```bash
   python "<skill-dir>/scripts/query.py" read <slug>
   ```
4. **直接下载模板/资料附件（`.zip` / `.tex` / `.pdf` 等）到当前目录或指定目录**：
   ```bash
   # 下载该页面的全部同步附件
   python "<skill-dir>/scripts/query.py" download <slug> --out ./

   # 或仅下载指定文件名
   python "<skill-dir>/scripts/query.py" download <slug> Note_revtex4-2.zip --out ./
   ```

> 若无法运行 Python，也可直接通过 HTTP 读取索引页：
> - 主地址：`https://raw.githubusercontent.com/Misaka16384/ye-group-toolkit/main/kb/index.md`
> - 国内/校园网镜像：`https://cdn.jsdelivr.net/gh/Misaka16384/ye-group-toolkit@main/kb/index.md`

## 回复用户的要求

1. **以实时拉取到的最新文档为准**：涉及系统入口、截止时间、负责人、连接参数与操作步骤时，严格引用 `query.py` 返回的最新内容，不要凭旧记忆编造。
2. **附带网页原页链接**：如果页面包含需要下载的压缩包/模板附件或界面实拍图（如 LaTeX 模板、海报模板、报销截图），请在回复中贴出对应的 `https://yurucamp.notion.site/...` 直达链接方便用户打开下载。
3. **维护与反馈**：工具箱维护人为 [Jie-Yu Zhang](https://github.com/Misaka16384)；如用户发现资料过时或想补充内容，可提示联系维护人更新 Notion 源页面。
