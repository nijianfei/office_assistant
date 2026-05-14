# 办公助手 - Web 自动化工具

基于 Python、PyQt6 和 DrissionPage 的内网系统 Web 自动化工具

---

## 📁 项目结构

```
office_assistant_new/
├── main.py                    # 程序入口
├── 启动程序.bat              # Windows 启动脚本
├── requirements.txt           # 依赖包清单
├── build.py                   # 集成混淆的构建脚本
├── build_simple.py            # 简单构建脚本（无混淆）
├── cleanup.py                 # 项目清理脚本
├── app.ico                    # 应用图标
├── version.json               # 版本信息
├── config/                    # 配置文件目录
│   └── config.yaml           # 应用配置
├── data/                      # 数据目录
│   ├── example_db.sqlite     # 示例数据库
│   ├── license.dat           # 许可证文件
│   └── trial.dat             # 试用数据
├── logs/                      # 日志目录
└── src/                       # 源代码目录
    ├── core/                 # 核心模块
    │   ├── browser_manager.py    # DrissionPage 浏览器管理
    │   ├── business_base.py      # 业务基类与自动注册
    │   └── scheduler.py          # 任务调度器
    ├── business/             # 业务模块（可混淆）
    │   └── baidu_test.py         # 百度搜索测试业务
    ├── gui/                  # 界面模块
    │   ├── main_window.py        # 主窗口
    │   ├── account_window.py     # 账号管理窗口
    │   ├── license_dialog.py     # 许可证对话框
    │   └── styles.py             # UI 样式
    ├── models/               # 数据模型
    │   ├── database.py           # 数据库连接
    │   ├── account.py            # 账号模型
    │   └── task.py               # 任务模型
    └── utils/                # 工具模块
        ├── logger.py             # 日志工具
        ├── license_manager.py    # 许可证管理
        ├── license_generator.py  # 许可证生成器
        ├── trial_manager.py      # 试用期管理
        └── version.py            # 版本管理
```

---

## ✨ 功能特性

### 账号管理
- ✅ 新增、编辑、删除账号
- ✅ 启用/禁用账号状态
- ✅ 子窗口配置管理

### 任务管理
- ✅ 任务列表展示与管理
- ✅ 三种调度方式：
  - 间隔执行
  - 固定时间
  - Cron 表达式
- ✅ 多选批量操作
- ✅ 实时查看任务日志

### 业务自动注册
- ✅ 开发环境：自动扫描业务目录
- ✅ 打包环境：预设业务列表导入
- ✅ `@business` 装饰器显式注册

### 许可证机制
- ✅ 90天试用期（离线验证）
- ✅ 硬件指纹绑定
- ✅ 时间回滚检测
- ✅ 累计运行时长限制

### 安全特性
- ✅ PyArmor 代码混淆支持
- ✅ AES-256 数据加密
- ✅ HMAC 完整性验证

---

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| UI | PyQt6 | 扁平化蓝色系界面 |
| 浏览器 | DrissionPage | 新一代 Web 自动化工具 |
| 数据库 | SQLAlchemy + SQLite | 轻量级嵌入式数据库 |
| 任务调度 | APScheduler | 灵活的定时任务管理 |
| 代码混淆 | PyArmor | 保护业务逻辑代码 |
| 打包工具 | PyInstaller | 单文件 EXE 打包 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动程序

**方式1：使用启动脚本**
```bash
双击运行：启动程序.bat
```

**方式2：命令行启动**
```bash
python main.py
```

---

## 🔧 开发指南

### 添加新业务

在 `src/business/` 目录下创建新的业务类：

```python
from src.core.business_base import BaseBusiness, business

@business
class MyBusiness(BaseBusiness):
    def get_name(self):
        return "my_business"
    
    def get_display_name(self):
        return "我的业务"
    
    def execute(self, browser, **kwargs):
        # 业务逻辑
        browser.get("https://example.com")
        return True
```

### 测试浏览器

```bash
# 官方文档测试
python test_drissionpage.py

# 浏览器管理器测试
python test_browser_manager.py
```

---

## 📦 构建指南

### 构建未混淆版本

```bash
python build_simple.py
```

### 构建混淆版本

```bash
python build.py
```

构建产物位于 `dist-obfuscated/dist/` 目录

### 清理项目

```bash
python cleanup.py
```

清理内容包括：
- 构建产物（`build/`, `dist/`, `dist-obfuscated/`）
- Python 缓存（`__pycache__/`, `.pyc` 文件）
- 日志文件（`logs/` 目录）
- 临时文件（`trial.dat`, `debug.log` 等）

---

## 📁 文件说明

| 文件/目录 | 说明 | 是否可删除 |
|-----------|------|-----------|
| `build/` | PyInstaller 临时构建目录 | ✅ 可删除 |
| `dist/` | 未混淆版本输出目录 | ✅ 可删除 |
| `dist-obfuscated/` | 混淆版本输出目录 | ✅ 可删除 |
| `logs/` | 日志文件目录 | ⚠️ 建议定期清理 |
| `__pycache__/` | Python 字节码缓存 | ✅ 可删除 |
| `*.pyc` | Python 编译文件 | ✅ 可删除 |
| `*.log` | 日志文件 | ✅ 可删除 |
| `trial.dat` | 试用数据文件 | ⚠️ 删除后重置试用期 |
| `.idea/` | IDE 配置目录 | ✅ 可删除（开发环境） |

---

## 📝 许可证生成

```bash
python -m src.utils.license_generator --fingerprint <指纹> --username <用户名> --days <天数>
```

示例：
```bash
python -m src.utils.license_generator -f "abc123" -u "张三" -d 365
```

---

## 📚 参考文档

- DrissionPage 官方文档：https://drissionpage.cn
- PyQt6 文档：https://www.riverbankcomputing.com/software/pyqt/
- APScheduler：https://apscheduler.readthedocs.io
- PyArmor：https://pyarmor.readthedocs.io

---

## 📄 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-05 | 初始版本 |

---

## 📞 技术支持

如有问题，请查看项目日志文件 `logs/office_assistant_*.log`
