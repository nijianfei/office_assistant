#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号管理窗口
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QTextEdit, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from src.models.account import AccountManager
from src.gui.styles import apply_stylesheet

class AccountWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("账号管理")
        self.setMinimumSize(800, 500)
        
        self.account_manager = AccountManager()
        
        self.init_ui()
        apply_stylesheet(self)
        self.load_accounts()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("账号管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("新增账号")
        self.add_btn.clicked.connect(self._add_account)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑账号")
        self.edit_btn.clicked.connect(self._edit_account)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除账号")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_account)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 账号表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "账号名称", "用户名", "URL", "描述", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_accounts(self):
        """加载账号列表"""
        self.table.setRowCount(0)
        accounts = self.account_manager.get_all_accounts()
        
        for account in accounts:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(account.id)))
            self.table.setItem(row, 1, QTableWidgetItem(account.name))
            self.table.setItem(row, 2, QTableWidgetItem(account.username))
            self.table.setItem(row, 3, QTableWidgetItem(account.url or ""))
            self.table.setItem(row, 4, QTableWidgetItem(account.description or ""))
            
            status = "启用" if account.is_enabled else "禁用"
            status_item = QTableWidgetItem(status)
            if account.is_enabled:
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)
    
    def _add_account(self):
        """新增账号"""
        dialog = AccountEditDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.account_manager.add_account(
                name=data['name'],
                username=data['username'],
                password=data['password'],
                url=data['url'],
                description=data['description']
            )
            self.load_accounts()
    
    def _edit_account(self):
        """编辑账号"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择要编辑的账号")
            return
        
        row = selected_rows[0].row()
        account_id = int(self.table.item(row, 0).text())
        account = self.account_manager.get_account(account_id)
        
        if account:
            dialog = AccountEditDialog(self, account)
            if dialog.exec():
                data = dialog.get_data()
                self.account_manager.update_account(account_id, **data)
                self.load_accounts()
    
    def _delete_account(self):
        """删除账号"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "提示", "请选择要删除的账号")
            return
        
        row = selected_rows[0].row()
        account_id = int(self.table.item(row, 0).text())
        account_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除账号 '{account_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.account_manager.delete_account(account_id):
                QMessageBox.information(self, "提示", "删除成功")
                self.load_accounts()
            else:
                QMessageBox.error(self, "错误", "删除失败")

class AccountEditDialog(QDialog):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.setWindowTitle("编辑账号" if account else "新增账号")
        self.setMinimumSize(400, 350)
        
        self.account = account
        
        self.init_ui()
        apply_stylesheet(self)
        
        if account:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 账号名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("账号名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入账号名称")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("请输入用户名")
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("请输入密码")
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("请输入登录地址")
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)
        
        # 描述
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("请输入账号描述")
        self.desc_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        """加载账号数据"""
        if self.account:
            self.name_edit.setText(self.account.name)
            self.username_edit.setText(self.account.username)
            self.password_edit.setText(self.account.password)
            self.url_edit.setText(self.account.url or "")
            self.desc_edit.setText(self.account.description or "")
    
    def get_data(self):
        """获取表单数据"""
        return {
            'name': self.name_edit.text(),
            'username': self.username_edit.text(),
            'password': self.password_edit.text(),
            'url': self.url_edit.text(),
            'description': self.desc_edit.toPlainText()
        }
    
    def accept(self):
        """验证并确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入账号名称")
            return
        
        if not self.username_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入用户名")
            return
        
        if not self.password_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入密码")
            return
        
        super().accept()
