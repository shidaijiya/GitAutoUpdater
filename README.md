# GitAutoUpdater

## 项目概述

`GitAutoUpdater` 是一个自动化更新脚本，用于从 GitHub 仓库下载最新版本的程序包，检查当前版本并进行更新，适用于 Linux 环境。通过读取配置文件并使用 GitHub API 获取最新的发布版本，脚本可以自动下载并安装更新包，并在后台启动程序。该脚本支持代理配置、日志记录、进程管理以及自动更新本地版本记录的功能。

## 功能

- **版本检查**：从指定的 GitHub 仓库获取最新的发布版本。
- **自动下载**：下载最新的程序包并解压安装。
- **停止程序**：在更新前自动停止当前运行的程序（如果有）。
- **后台运行**：更新完成后，自动将程序在后台运行。
- **更新版本记录**：自动更新 `update_config.json` 配置文件中的版本号。
- **日志记录**：自动记录更新过程中的详细日志，便于追踪和调试。
- **支持代理**：支持设置 HTTP/HTTPS 代理。
- **支持多个程序更新**：可以在一个配置文件中同时配置多个程序，批量更新。

## 环境要求

- Python 3.x
- `requests` 库（用于与 GitHub API 交互）
- `wget` 工具（用于下载文件）
- `tar`（用于解压包）
- `pgrep` 和 `kill`（用于管理进程）

### 必要依赖

在运行脚本之前，请确保安装以下 Python 库：

```bash
pip install requests wget
```

## 配置文件

### `update_config.json`

`GitAutoUpdater` 使用 `update_config.json` 配置文件来存储待更新的程序信息。该文件包括 GitHub 仓库的 `owner`、`repo`、`pkg_name`、`prog_name` 和当前版本 `current_version`。其中，`current_version` 字段是可选的，如果为空，脚本会认为没有本地版本记录。

以下是配置文件的示例结构：

```json
[
  {
    "owner": "exampleOwner",
    "repo": "exampleRepo",
    "pkg_name": "example_program_v1.0.tar.gz",
    "prog_name": "example_program",
    "current_version": "v1.0"
  },
  {
    "owner": "anotherOwner",
    "repo": "anotherRepo",
    "pkg_name": "another_program_v3.0.tar.gz",
    "prog_name": "another_program"
  }
]
```

- `owner`: GitHub 仓库的所有者 **（必填）**。
- `repo`: GitHub 仓库名 **（必填）**。
- `pkg_name`: 下载的程序包文件名 **（必填）**。
- `prog_name`: 程序的主执行文件名 **（必填）**。
- `current_version`: 当前安装的版本号 **（可选）**。如果没有指定，脚本会自动认为没有版本信息，开始进行更新。

## 使用说明

### 1. 配置 `update_config.json`

首先，您需要根据您的需求修改配置文件 `update_config.json`，以指定您要更新的程序信息，包括 GitHub 仓库、程序包文件名、执行程序名及当前版本。

#### 示例

```json
[
  {
    "owner": "myUser",
    "repo": "myRepo",
    "pkg_name": "my_program_v2.0.tar.gz",
    "prog_name": "my_program",
    "current_version": "v1.5"
  },
  {
    "owner": "anotherUser",
    "repo": "anotherRepo",
    "pkg_name": "another_program_v3.0.tar.gz",
    "prog_name": "another_program"
  }
]
```

在上面的示例中，`current_version` 是可选的。如果没有指定，脚本会假定您没有本地版本记录，直接进行更新。

### 2. 设置代理（可选）

如果您的网络环境需要代理访问 GitHub，请确保设置好 HTTP 和 HTTPS 代理。可以在操作系统的环境变量中设置 `HTTP_PROXY` 和 `HTTPS_PROXY`，或者直接在脚本中配置。

### 3. 执行脚本

运行脚本前，确保系统安装了 Python 3 及所需的库。可以通过以下命令安装 `requests` 和 `wget` 库：

```bash
pip install requests wget
```

然后，运行 `run.py` 脚本进行更新：

```bash
python run.py
```

脚本会自动检查配置文件中列出的每个程序仓库，获取最新版本，下载程序包并解压。如果本地版本不是最新的，脚本会停止当前程序，更新程序并在后台重新启动。

### 4. 日志记录

脚本会自动生成并维护日志文件 `./log/update.log`，记录每次更新的过程，包括成功、失败的操作及错误信息。您可以查看日志来了解每次更新的详细情况。无需手动设置日志路径，所有日志都将保存在 `./log/update.log` 文件中。

### 5. 更新本地版本

在每次成功更新并启动程序后，脚本会自动更新 `update_config.json` 中的 `current_version` 字段为最新的版本号。这意味着下次运行脚本时，`current_version` 将与 GitHub 上的版本号保持同步。

## 设置定时任务（Cron）

为了确保程序定期自动更新，您可以将该脚本设置为定时任务。以下是如何在 Linux 系统中使用 `cron` 设置定时任务。

### 1. 编辑 Cron 表

首先，打开您的 `crontab` 配置文件：

```bash
crontab -e
```

### 2. 添加定时任务

在 `crontab` 文件中添加一行配置，指定脚本的运行频率。以下是一些常见的定时任务示例：

- **每天凌晨 3 点运行：**

  ```bash
  0 3 * * * /usr/bin/python3 /path/to/run.py
  ```

- **每小时运行一次：**

  ```bash
  0 * * * * /usr/bin/python3 /path/to/run.py
  ```

- **每周一凌晨 3 点运行：**

  ```bash
  0 3 * * 1 /usr/bin/python3 /path/to/run.py
  ```

- **每月 1 号凌晨 3 点运行：**

  ```bash
  0 3 1 * * /usr/bin/python3 /path/to/run.py
  ```

### 3. 保存并退出

编辑完定时任务后，保存并退出编辑器。然后，`cron` 服务会自动加载新的任务。


```bash
tail -f ./log/update.log
```

## 常见问题

### Q1: 如何查看更新日志？

日志文件存储在 `./log/update.log` 中。您可以使用任何文本编辑器或命令行工具查看该文件：

```bash
cat ./log/update.log
```

### Q2: 我可以同时更新多个程序吗？

是的，您可以在 `update_config.json` 中配置多个 GitHub 仓库，脚本会依次处理每个仓库的更新。每个程序的更新流程是独立的。

### Q3: 如何设置 HTTP/HTTPS 代理？

本脚本会默认检测系统代理并使用，如果您的网络环境需要通过代理访问 GitHub，您可以修改环境变量配置代理。示例：

```bash
export HTTP_PROXY="http://your_proxy:port"
export HTTPS_PROXY="http://your_proxy:port"
```

### Q4: 如何自定义脚本中的安装路径？

您可以在脚本中修改 `inst_dir` 变量，来指定自定义的程序安装路径。




