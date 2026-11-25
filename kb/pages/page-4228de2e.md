# 🖥️ 课题组服务器与超算资源指南

- **网页直达（含附件/截图）**：https://yurucamp.notion.site/4228de2e6f7d8146af83e7d14d2d9c8d
- **分类**：计算与工具
- **标签**：指南, 新人必看
- **所属页面**：YE Group Toolkit
- **Notion 最后更新**：2026-11-25T07:12:00.000Z

---

> 🖥️ **课题组服务器与超算资源指南**
> 汇总课题组可供使用的本地 CPU 服务器与国家超算广州中心「天河星逸」计算资源、SSH 连接配置、使用规范与账号密码申请方式。


> 👤 **账号密码与负责人**
> - **当前负责人**：**王晗燮** 同学
> - **课题组本地服务器密码**：由 **王晗燮** 同学统一管理，配置好下方 SSH 后请直接向他获取登录密码。
> - **超算账号与大额机时**：如需开通天河星逸账号、获取登录密钥，或有大额机时/GPU 采购需求，请联系 **王晗燮** 同学（大额采购需同时与叶老师沟通）。


## 📊 资源概览


| 资源 | 类型 | 主要配置 | 适用场景 | 费用与额度 |
| --- | --- | --- | --- | --- |
| **课题组本地服务器** | 组内共享 CPU 服务器 | 52 物理核（2× Xeon 8263C）、约 187 GB 内存、本地共享存储 | 日常免费 CPU 数值计算、代码调试与中等规模多核并行 | 免费（组内共享） |
| **国家超算广州中心「天河星逸」** | 国家级 HPC 集群（Slurm） | 单节点 64–88 核、500 GiB 内存、最长运行 7 天 | 大规模扫参、大内存任务与长时运行 | 共享课题组机时 |


---


## 1️⃣ 课题组本地服务器

课题组共享的本地 CPU 服务器，适合日常数值计算与中等规模多核任务，不消耗超算机时。


### 🔌 SSH 连接方式

将以下配置添加到本机 `~/.ssh/config`（别名 `ye-server` 可按个人习惯自定义），保存后执行 `ssh ye-server` 登录。**登录密码由王晗燮同学管理，请向他获取。**

**Windows**（需先安装 [Git for Windows](https://git-scm.com/downloads) 以使用 `connect.exe`）：


```text
Host ye-server
    HostName manager.sysuphys.com
    User manager
    ProxyCommand C:\Progra~1\Git\mingw64\bin\connect.exe -H 8.163.108.34:2222 %h %p
```

**macOS / Linux**（使用系统自带 `nc`）：


```text
Host ye-server
    HostName manager.sysuphys.com
    User manager
    ProxyCommand nc -X connect -x 8.163.108.34:2222 %h %p
```

- **Windows 终端提示**：请优先使用 **PowerShell / Windows Terminal** 自带的 OpenSSH 执行 `ssh ye-server` 与 `scp`。Git Bash 默认 `ssh` 解析 Windows 路径容易报错；如在 Git Bash 中使用，请显式调用 `/c/Windows/System32/OpenSSH/ssh.exe ye-server`。

### ⚙️ 硬件与使用规范

- **硬件规格**：2 × Intel Xeon Platinum 8263C（**52 物理核**，2 个 NUMA 节点）、**约 187 GB 内存**、本地共享磁盘。
- **共享使用规范**：
  - 启动重负载任务前请先检查当前 CPU 与内存占用（`htop`、`free -h`），为系统及同组同学预留适量核心和内存，避免影响正在运行的任务。
  - 请在个人独立目录下工作，切勿误杀他人进程或修改他人目录。
- **Python 环境小贴士**：
  - 系统自带旧版 Anaconda 的 MKL 在复数 BLAS（如复数 `eigsh` / `np.vdot`）上可能存在兼容问题，推荐自建 Python `venv` 并安装 PyPI 版 `numpy` / `scipy`（OpenBLAS）。

---


## 2️⃣ 国家超算广州中心「天河星逸」

国家超算广州中心高性能 CPU 集群，采用 Slurm 作业调度系统，可配合 [星光平台](https://starlight.nscc-gz.cn/) 管理作业与查看机时。账号开通与登录配置请联系 **王晗燮** 同学。


### 常用 CPU 队列


| 分区 | 单节点核数 | 单节点内存 | 最长运行时间 | 说明 |
| --- | --- | --- | --- | --- |
| `debug` | 64 核（Xeon 8358P） | 500 GiB | 30 分钟 | 快速测试队列 |
| `deimos` | 64 核（Xeon 8358P） | 500 GiB | 7 天 | 主力生产队列（1.0 倍核时权重） |
| `phobos` | 88 核（Xeon 8458P） | 500 GiB | 7 天 | 高性能队列（1.2 倍核时权重） |


### 使用注意事项

- **整节点独占计费**：Slurm 作业按整节点独占计费（无论申请多少核都占用整张 64/88 核节点）。请尽量将多个独立子任务打包进同一节点作业中，避免核心空转浪费课题组机时。
- **大规模任务报备**：提交大规模多节点扫参前，建议先在 `debug` 队列测试通过，并与 **王晗燮** 同学确认当前机时余额。
- **常用软件环境**：通过 `module load` 加载 `anaconda3`、`python`、`julia`、`gcc`、`intel oneAPI` 等预装环境。
- **密钥有效期**：星逸 `.id` 登录密钥若连续 3 个月未使用会自动失效，失效后可登录 [星光平台](https://starlight.nscc-gz.cn/) 重新下载。

> ⚠️ **关于 GPU 资源说明**
> 课题组目前在超算中心仅采购了 **CPU 资源**，暂未开通 GPU 节点。如课题确有超算 GPU 需求，请先与叶老师及 **王晗燮** 同学沟通，由负责人统一对接开通。
