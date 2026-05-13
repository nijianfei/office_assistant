#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公助手 - 主入口
内网系统Web端自动化操作工具
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.utils.license_manager import LicenseManager
from src.utils.logger import logger
from src.models.task import TaskManager
from src.core.business_base import discover_and_register_businesses

def init_demo_task():
    """初始化Demo任务"""
    task_manager = TaskManager()
    tasks = task_manager.get_all_tasks()
    
    # 如果没有任务，创建Demo任务
    if not tasks:
        logger.info("首次启动，创建Demo任务")
        task_manager.add_task(
            name="百度搜索测试",
            business_name="baidu_test",
            schedule_type="interval",
            interval_seconds=300,
            params={"search_keyword": "办公助手", "switch_tabs": True, "tab_list": "资讯"},
            is_enabled=True
        )

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("办公助手启动")
    logger.info("=" * 50)
    
    # 检查许可证
    license_manager = LicenseManager()
    if not license_manager.is_valid():
        QMessageBox.critical(None, "许可证过期", "试用期限已过，请联系管理员")
        return
    
    remaining_days = license_manager.get_remaining_days()
    logger.info(f"许可证检查: 有效, 到期时间: {license_manager.get_end_date()}")
    
    # 发现业务
    discover_and_register_businesses()
    
    # 初始化Demo任务
    init_demo_task()
    
    # 启动应用
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # 设置许可证信息
    end_date = license_manager.get_end_date()
    window.license_label.setText(f"试用版 - 剩余 {remaining_days} 天")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
