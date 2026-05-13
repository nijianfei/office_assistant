#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
办公助手 - 主入口
内网系统Web端自动化操作工具
"""

import sys
import os
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from src.gui.main_window import MainWindow
from src.gui.license_dialog import LicenseActivationDialog
from src.utils.license_manager import LicenseManager
from src.utils.trial_manager import TrialManager
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
    start_time = time.time()
    logger.info("=" * 50)
    logger.info("办公助手启动")
    logger.info("=" * 50)
    
    # 创建应用实例（需要先创建QApplication才能显示对话框）
    app = QApplication(sys.argv)
    
    # 创建试用管理器（首次启动会生成硬件指纹并创建试用记录）
    trial_manager = TrialManager()
    
    # 检查许可证
    license_manager = LicenseManager()
    license_valid = license_manager.is_valid()
    
    # 如果许可证无效，检查试用
    if not license_valid:
        logger.warning("许可证无效，检查试用状态")
        
        # 检查试用是否有效
        if not trial_manager.is_trial_valid():
            logger.error("试用已过期")
            
            # 显示激活对话框，最多尝试3次
            for attempt in range(3):
                dialog = LicenseActivationDialog()
                result = dialog.exec()
                
                if result == 1:  # 用户点击了激活并成功
                    # 重新加载许可证
                    license_manager = LicenseManager()
                    if license_manager.is_valid():
                        license_valid = True
                        break
                
                # 用户取消或激活失败
                if attempt == 2:  # 最后一次尝试失败
                    QMessageBox.critical(None, "试用过期", 
                        "试用期限已过，请联系管理员获取激活码\n\n"
                        "检测到以下异常可能导致试用过期：\n"
                        "- 系统时间被回滚\n"
                        "- 时间大幅跳变\n"
                        "- 超过90天试用期限\n"
                        "- 累计运行时长超过720小时")
                    return
    
    if license_valid:
        # 正式版许可证
        license_info = license_manager.get_license_info()
        license_type = license_info.get('type', '正式版')
        remaining_days = license_manager.get_remaining_days()
        logger.info(f"许可证检查: 有效 ({license_type}), 到期时间: {license_manager.get_end_date()}")
    else:
        # 试用版
        trial_info = trial_manager.get_trial_info()
        remaining_days = trial_info['remaining_days']
        remaining_hours = trial_info['remaining_hours']
        logger.info(f"试用检查: 有效, 剩余 {remaining_days} 天 / {remaining_hours:.1f} 小时")
    
    # 发现业务
    discover_and_register_businesses()
    
    # 初始化Demo任务
    init_demo_task()
    
    # 启动应用
    window = MainWindow()
    window.show()
    
    # 设置许可证/试用信息
    if license_valid:
        license_info = license_manager.get_license_info()
        license_type = license_info.get('type', '正式版')
        if license_type == '正式版':
            window.license_label.setText(f"正式版 - 用户: {license_info.get('username', '')}")
        else:
            window.license_label.setText(f"试用版 - 剩余 {remaining_days} 天")
    else:
        trial_info = trial_manager.get_trial_info()
        window.license_label.setText(f"试用版 - 剩余 {trial_info['remaining_days']} 天 / {trial_info['remaining_hours']:.1f} 小时")
    
    # 更新累计运行时长
    run_duration = time.time() - start_time
    trial_manager.update_run_duration(run_duration)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
