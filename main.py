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
from src.gui.license_dialog import LicenseActivationDialog
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
    
    # 创建应用实例（需要先创建QApplication才能显示对话框）
    app = QApplication(sys.argv)
    
    # 检查许可证
    license_manager = LicenseManager()
    
    # 如果许可证无效，显示激活对话框
    if not license_manager.is_valid():
        logger.warning("许可证无效或已过期")
        
        # 显示激活对话框，最多尝试3次
        for attempt in range(3):
            dialog = LicenseActivationDialog()
            result = dialog.exec()
            
            if result == 1:  # 用户点击了激活并成功
                # 重新加载许可证
                license_manager = LicenseManager()
                if license_manager.is_valid():
                    break
                
            # 用户取消或激活失败
            if attempt == 2:  # 最后一次尝试失败
                QMessageBox.critical(None, "许可证过期", "试用期限已过，请联系管理员获取激活码")
                return
    
    remaining_days = license_manager.get_remaining_days()
    logger.info(f"许可证检查: 有效, 到期时间: {license_manager.get_end_date()}")
    
    # 发现业务
    discover_and_register_businesses()
    
    # 初始化Demo任务
    init_demo_task()
    
    # 启动应用
    window = MainWindow()
    window.show()
    
    # 设置许可证信息
    end_date = license_manager.get_end_date()
    license_info = license_manager.get_license_info()
    license_type = license_info.get('type', 'trial')
    if license_type == '正式版':
        window.license_label.setText(f"正式版 - 用户: {license_info.get('username', '')}")
    else:
        window.license_label.setText(f"试用版 - 剩余 {remaining_days} 天")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
