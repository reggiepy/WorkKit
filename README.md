# WorkKit

[![python version](https://img.shields.io/badge/Python-3.10-success.svg?style=flat)]()
[![build status](https://img.shields.io/badge/build-pass-success.svg?style=flat)]()

---

WorkKit 是一款基于 Python 3.10 和 PySide6 构建的桌面办公工具包，旨在解决日常办公中常见的文件处理和数据管理问题。

## 📸 界面预览

![界面预览](docs/imgs/1.png)

## ✨ 主要功能

*   **PDF 处理**: 包含 PDF 合并、单页提取、发票处理等功能 (基于 PyMuPDF/PyPDF)。
*   **办公辅助**: 提供各类办公自动化工具。
*   **本地数据管理**: 使用 SQLAlchemy + SQLite 进行本地数据存储。
*   **现代化 UI**: 基于 PySide6 (Qt) 的现代化图形界面。

## 🛠️ 安装说明 (Installation)

本项目使用 [Poetry](https://python-poetry.org/) 或 uv 进行依赖管理。

### 前置要求
*   Python >= 3.10

### 安装依赖

```bash
uv sync
```

## 🚀 运行 (Usage)

在项目根目录下运行以下命令启动应用：

```bash
python src/main.py
```

## 📦 打包构建 (Build)

项目包含用于 Windows 平台的打包脚本（基于 PyInstaller）。

```bash
build.bat
```
*注意：`build.bat` 中包含硬编码路径，使用前请根据本地环境修改 `PYTHONENVNAME` 和相关路径。*

## 🏗️ 技术架构 (Architecture)

*   **核心语言**: Python 3.10+
*   **GUI 框架**: PySide6
*   **ORM 框架**: SQLAlchemy (配合 Alembic 进行数据库迁移)
*   **打包工具**: PyInstaller

### 目录结构简述

*   `src/`: 源代码目录
    *   `controllers/`: 业务逻辑控制
    *   `models/`: 数据库模型
    *   `views/`: 界面视图逻辑
    *   `ui/`: 界面布局定义
    *   `utils/`: 通用工具库
    *   `db/`: 数据库初始化与会话管理