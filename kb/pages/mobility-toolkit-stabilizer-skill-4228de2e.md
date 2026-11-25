# 🧮 mobility-toolkit：Stabilizer 模型计算 Skill

- **网页直达（含附件/截图）**：https://yurucamp.notion.site/4228de2e6f7d810ab7b4d7b03216930b
- **分类**：计算与工具
- **标签**：AI Skill, Stabilizer
- **所属页面**：YE Group Toolkit
- **Notion 最后更新**：2026-11-25T07:12:00.000Z

---

> 🧮 **mobility-toolkit：Stabilizer 模型计算 Skill**
> 面向平移不变与有限 Stabilizer 码的边界感知计算工具箱，提供 Python、CLI、MCP 与 8 个专用 Agent Skill 共享的统一计算接口，支持同调代数（Macaulay2）后端。


- 🔗 [https://github.com/Misaka16384/mobility-toolkit](https://github.com/Misaka16384/mobility-toolkit)


## ✨ 核心计算能力

- **有限广义泡利码（Generalized-Pauli Codes）**：支持素数、合数与混合局域维度；计算中心化子、逻辑算符群与基态简并度（GSD）。
- **有限截断与边界代数**：显式有限截断、配对群、主投影及有界 $E_1$/$E_2$ 搜索。
- **精确胞腔相对同调**：面向显式有限胞腔对的精确相对同调计算。
- **周期 Laurent 表示与半空间**：定理范围内的荷模（charge-module）运算、定向有理半空间与源码锁定的边界基准。
- **有界 2D / 3D 边界候选枚举**：支持 NDJSON 分页流式输出（`service-stream`）与基于 `SQLiteCheckpointStore` 的可恢复断点。
- **分层缺陷与 Cheshire 分类**：端点、管状缺陷、节点关联；2D $\mathbb{Z}_2$ toric 码 Cheshire/后代分类与有序融合、有限格点/线路见证、3+1D 静态参考与分级 X-cube 支撑候选。
- **严格可追溯与边界诚实**：每次计算结果均附带适用范围、精确性、假设条件、证书、溯源与警告；超出支持范围的数学问题会返回结构化 `unsupported`，绝不静默近似。

## 🧩 内置 8 个专用 Skill


| Skill 名称 | 主要算子族 | 适用范围 |
| --- | --- | --- |
| `mt-finite-code` | `finite.code.*` | 有限广义泡利算术、中心化子、逻辑群与基态简并度（GSD） |
| `mt-boundary-algebra` | `boundary.finite.*`、`boundary.enumeration.*` | 显式有限截断、配对群、主投影与有界 E1/E2 搜索 |
| `mt-relative-homology` | `topology.relative_homology` | 显式有限胞腔对的精确相对同调 |
| `mt-halfspace` | `boundary.halfspace.*` | 定向单侧 Laurent 半空间与边界基准测试 |
| `mt-gapped-boundary-2d` | `boundary.completion2d.*` | 有限度规凝聚与显式有界局域补全 |
| `mt-gapped-boundary-3d` | `boundary.symbolic3d.*` | E1/E2 与有界符号 E3 候选搜索 |
| `mt-defect` | `defects.*` | 有限分层边界、端点、管状缺陷与节点关联 |
| `mt-cheshire` | `defects.cheshire.*` | 2D toric/阿贝尔分类与融合、线路检验、3+1D 参考与 X-cube 候选 |


## 📦 安装与环境要求

- **依赖环境**：Python 3.10+。**Macaulay2** 仅在需要该后端的运算（如周期 Laurent / Ext 计算）时必需，工具会按顺序自动探测：`MOBILITY_M2_CMD` → `MOBILITY_M2_DOCKER_IMAGE` → 系统 `PATH` 中的原生 `M2` → Windows WSL（`MOBILITY_M2_WSL_DISTRO`）。

```bash
# 安装工具包并部署项目级 Skill
pipx install "git+https://github.com/Misaka16384/mobility-toolkit.git"
mobility-toolkit install

# 可选：同时配置 MCP 服务
mobility-toolkit install --mcp
```

支持宿主包括 **Claude Code**（`.claude/skills/`）、**OpenCode**（`.opencode/skills/`）、**Codex**（`.agents/skills/`）与 **Antigravity 2.0**（`.agents/skills/`）。


## 🚀 常用命令


```bash
# 查看所有算子目录与严格 JSON 输入契约
mobility-toolkit service-catalog

# 诊断 Macaulay2 后端并进行冒烟测试
mobility-toolkit doctor

# 执行标准计算请求
mobility-toolkit service --request '{
  "schema": "mobility_toolkit.service_request.v1",
  "schema_version": "2",
  "operation": "finite.code.capabilities",
  "input_data": {}
}'

# 更新工具包版本
mobility-toolkit self-update
```
