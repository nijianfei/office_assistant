#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证激活对话框
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from src.utils.license_manager import LicenseManager


class LicenseActivationDialog(QDialog):
    """许可证激活对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("许可证激活")
        self.setFixedSize(500, 400)
        self.license_manager = LicenseManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 机器码区域
        machine_group = QGroupBox("机器码")
        machine_layout = QVBoxLayout()
        
        self.machine_code_label = QLabel("您的机器码：")
        machine_layout.addWidget(self.machine_code_label)
        
        self.machine_code_edit = QLineEdit()
        self.machine_code_edit.setText(self.license_manager.get_machine_fingerprint())
        self.machine_code_edit.setReadOnly(True)
        self.machine_code_edit.setStyleSheet("font-family: monospace; font-size: 12px;")
        machine_layout.addWidget(self.machine_code_edit)
        
        self.copy_btn = QPushButton("复制机器码")
        self.copy_btn.clicked.connect(self.copy_machine_code)
        machine_layout.addWidget(self.copy_btn)
        
        machine_group.setLayout(machine_layout)
        layout.addWidget(machine_group)
        
        # 激活码区域
        activate_group = QGroupBox("激活码")
        activate_layout = QVBoxLayout()
        
        self.activate_code_label = QLabel("请输入激活码：")
        activate_layout.addWidget(self.activate_code_label)
        
        self.activate_code_edit = QTextEdit()
        self.activate_code_edit.setPlaceholderText("将生成的激活码粘贴到这里...")
        self.activate_code_edit.setFixedHeight(80)
        activate_layout.addWidget(self.activate_code_edit)
        
        activate_group.setLayout(activate_layout)
        layout.addWidget(activate_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.activate_btn = QPushButton("激活")
        self.activate_btn.clicked.connect(self.activate_license)
        btn_layout.addWidget(self.activate_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 提示信息
        hint_label = QLabel(
            "<font color='gray'>提示：请将机器码发送给管理员获取激活码</font>"
        )
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
        
    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        clipboard = self.parent().clipboard() if self.parent() else None
        if clipboard:
            clipboard.setText(self.machine_code_edit.text())
            QMessageBox.information(self, "成功", "机器码已复制到剪贴板")
        else:
            # 备用方案
            import pyperclip
            pyperclip.copy(self.machine_code_edit.text())
            QMessageBox.information(self, "成功", "机器码已复制到剪贴板")
    
    def activate_license(self):
        """激活许可证"""
        license_code = self.activate_code_edit.toPlainText().strip()
        
        if not license_code:
            QMessageBox.warning(self, "警告", "请输入激活码")
            return
        
        # 保存激活码到文件
        try:
            license_file = 'data/license.dat'
            os.makedirs(os.path.dirname(license_file), exist_ok=True)
            with open(license_file, 'w', encoding='utf-8') as f:
                f.write(license_code)
            
            # 验证许可证
            new_license_manager = LicenseManager()
            if new_license_manager.is_valid():
                QMessageBox.information(self, "成功", "许可证激活成功！程序将重启...")
                self.accept()
            else:
                QMessageBox.critical(self, "失败", "许可证无效或与当前机器不匹配")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存许可证失败: {str(e)}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = LicenseActivationDialog()
    dialog.exec()
