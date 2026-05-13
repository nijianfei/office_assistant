# 办公助手 - Web 自动化工具

基于 Python、PyQt6 和 DrissionPage 的内网系统 Web 自动化工具

## 项目结构

```
office_assistant_new/
├── main.py                    # 程序入口
├── 启动程序.bat              # Windows 启动脚本
├── requirements.txt           # 依赖包
├── test_drissionpage.py      # DrissionPage 官方测试
├── test_browser_manager.py   # 浏览器管理器测试
├── config/
├── data/
├── logs/
└── src/
    ├── core/
    │   ├── browser_manager.py      # DrissionPage 浏览器管理
    │   ├── business_base.py        # 业务基类与自动注册
    │   └── scheduler.py            # 任务调度器
    ├── business/
    │   └── baidu_test.py           # 百度搜索测试业务
    ├── gui/
    │   ├── main_window.py          # 主窗口
    │   ├── account_window.py       # 账号管理窗口
    │   └── styles.py               # UI 样式
    ├── models/
    │   ├── database.py             # 数据库
    │   ├── account.py              # 账号模型
    │   └── task.py                 # 任务模型
    └── utils/
        ├── logger.py               # 日志工具
        └── license_manager.py      # 许可证管理
```

## 功能特性

### ✅ 账号管理
- 新增、编辑、删除账号
- 启用/禁用账号
- 通过子窗口配置管理

### ✅ 任务管理
- 任务列表展示
- 支持三种调度方式：
  - 间隔执行
  - 固定时间
  - Cron 表达式
- 支持多选批量操作
- 实时查看任务日志

### ✅ 业务自动注册
- 自动发现业务目录
- 新增业务类自动注册
- 任务有效性配置

### ✅ 试用版机制
- 3个月试用期
- 许可证自动管理

## 技术栈

- **UI**: PyQt6 (扁平化蓝色青春系)
- **浏览器**: DrissionPage
- **数据库**: SQLAlchemy + SQLite
- **任务调度**: APScheduler

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动程序

方式1：使用启动脚本
```bash
双击运行：启动程序.bat
```

方式2：命令行启动
```bash
python main.py
```

### 测试浏览器

```bash
# 官方文档测试
python test_drissionpage.py

# 浏览器管理器测试
python test_browser_manager.py
```

## 使用说明

### 添加新业务

在 `src/business/` 目录下创建新的业务类，继承 `BaseBusiness`：

```python
from src.core.business_base import BaseBusiness

class MyBusiness(BaseBusiness):
    def get_name(self):
        return "my_business"
    
    def get_display_name(self):
        return "我的业务"
    
    def execute(self, browser, **kwargs):
        # 业务逻辑
        return True
```

重启程序后自动发现并注册新业务。

## 参考文档

- DrissionPage 官方文档：https://drissionpage.cn
- PyQt6 文档：https://www.riverbankcomputing.com/software/pyqt/
