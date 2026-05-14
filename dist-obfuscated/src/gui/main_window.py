#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView,
    QCheckBox, QDialog, QTextEdit, QComboBox, QLineEdit, QSpinBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from src.models.task import TaskManager
from src.models.account import AccountManager
from src.core.scheduler import TaskScheduler
from src.core.business_base import get_all_businesses
from src.gui.account_window import AccountWindow
from src.gui.styles import apply_stylesheet
from src.utils.logger import logger
from src.utils.version import get_full_version
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("办公助手")
        self.setMinimumSize(1000, 600)
        
        self.task_manager = TaskManager()
        self.account_manager = AccountManager()
        self.scheduler = TaskScheduler()
        
        self.selected_tasks = {}
        
        self.init_ui()
        apply_stylesheet(self)
        
        # 定时刷新任务列表
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_tasks)
        self.refresh_timer.start(5000)
        
        # 启动调度器
        self.scheduler.start()
        
        # 加载任务列表
        self.load_tasks()
    
    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 顶部按钮栏
        top_layout = QHBoxLayout()
        
        self.account_btn = QPushButton("账号管理")
        self.account_btn.clicked.connect(self._open_account_window)
        top_layout.addWidget(self.account_btn)
        
        top_layout.addStretch()
        
        self.version_label = QLabel(f"版本: {get_full_version()}")
        self.version_label.setStyleSheet("font-size: 12px; color: #666;")
        top_layout.addWidget(self.version_label)
        
        self.license_label = QLabel()
        top_layout.addWidget(self.license_label)
        
        layout.addLayout(top_layout)
        
        # 标题
        title_label = QLabel("任务管理")
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # 操作按钮栏
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("新增任务")
        self.add_btn.clicked.connect(self._add_task)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑任务")
        self.edit_btn.clicked.connect(self._edit_task)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除任务")
        self.delete_btn.setObjectName("dangerBtn")
        self.delete_btn.clicked.connect(self._delete_task)
        button_layout.addWidget(self.delete_btn)
        
        self.run_btn = QPushButton("立即执行")
        self.run_btn.clicked.connect(self._run_task)
        button_layout.addWidget(self.run_btn)
        
        self.log_btn = QPushButton("查看日志")
        self.log_btn.clicked.connect(self._view_log)
        button_layout.addWidget(self.log_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 任务表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "", "ID", "任务名称", "业务类型", "调度方式", 
            "状态", "是否启用", "上次执行", "操作"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().resizeSection(0, 45)
        self.table.horizontalHeader().resizeSection(8, 70)  # 操作列宽度
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # 禁用编辑
        self.table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self.table)
    
    def _create_center_item(self, text):
        """创建居中对齐的表格项"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
        
    def load_tasks(self):
        """加载任务列表"""
        self.table.setRowCount(0)
        tasks = self.task_manager.get_all_tasks()
        
        for task in tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 复选框（居中显示）
            checkbox = QCheckBox()
            checkbox.setChecked(task.id in self.selected_tasks)
            checkbox.stateChanged.connect(lambda state, tid=task.id: self._toggle_task_select(tid, state))
            
            # 将复选框放入居中布局
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.addStretch()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.addStretch()
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # ID
            self.table.setItem(row, 1, self._create_center_item(str(task.id)))
            
            # 任务名称
            self.table.setItem(row, 2, self._create_center_item(task.name))
            
            # 业务类型
            business = get_all_businesses()
            business_name = task.business_name
            for b in business:
                if b.get_name() == task.business_name:
                    business_name = b.get_display_name()
                    break
            self.table.setItem(row, 3, self._create_center_item(business_name))
            
            # 调度方式
            schedule_desc = ""
            if task.schedule_type == 'interval':
                schedule_desc = f"间隔 {task.interval_seconds}秒"
            elif task.schedule_type == 'fixed_time':
                schedule_desc = f"定时 {task.fixed_time}"
            elif task.schedule_type == 'cron':
                schedule_desc = f"Cron {task.cron_expression}"
            self.table.setItem(row, 4, self._create_center_item(schedule_desc))
            
            # 状态
            status_item = self._create_center_item(task.status)
            if task.status == 'running':
                status_item.setForeground(Qt.GlobalColor.blue)
            elif task.status == 'success':
                status_item.setForeground(Qt.GlobalColor.green)
            elif task.status == 'failed':
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)
            
            # 是否启用
            enabled_item = self._create_center_item("是" if task.is_enabled else "否")
            if task.is_enabled:
                enabled_item.setForeground(Qt.GlobalColor.green)
            else:
                enabled_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 6, enabled_item)
            
            # 上次执行
            last_run = task.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if task.last_run_at else "从未执行"
            self.table.setItem(row, 7, self._create_center_item(last_run))
            
            # 操作按钮
            toggle_btn = QPushButton("启用" if not task.is_enabled else "禁用")
            toggle_btn.setObjectName("secondaryBtn")
            toggle_btn.setFixedSize(55, 20)  # 更小的按钮
            toggle_btn.setStyleSheet("font-size: 12px; padding: 0px;")
            toggle_btn.clicked.connect(lambda checked, tid=task.id: self._toggle_task_enabled(tid))
            
            # 创建容器布局来正确放置按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.addStretch()
            btn_layout.addWidget(toggle_btn)
            btn_layout.addStretch()
            
            self.table.setCellWidget(row, 8, btn_widget)
    
    def _on_cell_clicked(self, row, column):
        """点击单元格时触发复选框切换（操作列除外）"""
        if column == 8:  # 操作列不触发
            return
        
        # 获取包含复选框的容器
        container = self.table.cellWidget(row, 0)
        if container:
            # 查找容器中的复选框
            checkbox = container.findChild(QCheckBox)
            if checkbox:
                checkbox.toggle()
    
    def _toggle_task_select(self, task_id, state):
        """切换任务选择状态"""
        if state == Qt.CheckState.Checked.value:
            self.selected_tasks[task_id] = True
        else:
            self.selected_tasks.pop(task_id, None)
    
    def _toggle_task_enabled(self, task_id):
        """切换任务启用状态"""
        result = self.task_manager.toggle_task_enabled(task_id)
        if result is not None:
            self.scheduler.refresh_task(task_id)
            self.load_tasks()
    
    def _open_account_window(self):
        """打开账号管理窗口"""
        dialog = AccountWindow(self)
        dialog.exec()
    
    def _add_task(self):
        """新增任务"""
        dialog = TaskEditDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.task_manager.add_task(
                name=data['name'],
                business_name=data['business_name'],
                schedule_type=data['schedule_type'],
                interval_seconds=data.get('interval_seconds', 300),
                fixed_time=data.get('fixed_time'),
                cron_expression=data.get('cron_expression'),
                params=data.get('params', {}),
                account_id=data.get('account_id'),
                is_enabled=True
            )
            self.load_tasks()
    
    def _edit_task(self):
        """编辑任务"""
        if not self.selected_tasks:
            QMessageBox.warning(self, "提示", "请选择要编辑的任务")
            return
        
        task_ids = list(self.selected_tasks.keys())
        if len(task_ids) > 1:
            QMessageBox.warning(self, "提示", "只能选择一个任务进行编辑")
            return
        
        task_id = task_ids[0]
        task = self.task_manager.get_task(task_id)
        
        if task:
            dialog = TaskEditDialog(self, task)
            if dialog.exec():
                data = dialog.get_data()
                self.task_manager.update_task(task_id, **data)
                self.scheduler.refresh_task(task_id)
                self.load_tasks()
    
    def _delete_task(self):
        """删除任务"""
        if not self.selected_tasks:
            QMessageBox.warning(self, "提示", "请选择要删除的任务")
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(self.selected_tasks)} 个任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for task_id in self.selected_tasks.keys():
                self.scheduler.remove_task_from_schedule(task_id)
                self.task_manager.delete_task(task_id)
            
            self.selected_tasks.clear()
            self.load_tasks()
            QMessageBox.information(self, "提示", "删除成功")
    
    def _run_task(self):
        """立即执行任务"""
        if not self.selected_tasks:
            QMessageBox.warning(self, "提示", "请选择要执行的任务")
            return
        
        for task_id in self.selected_tasks.keys():
            self.scheduler.run_task_once(task_id, wait_complete=False)
        
        QMessageBox.information(self, "提示", "任务已提交执行")
        self.load_tasks()
    
    def _view_log(self):
        """查看任务日志"""
        if not self.selected_tasks:
            QMessageBox.warning(self, "提示", "请选择要查看日志的任务")
            return
        
        task_ids = list(self.selected_tasks.keys())
        if len(task_ids) > 1:
            QMessageBox.warning(self, "提示", "只能选择一个任务查看日志")
            return
        
        task_id = task_ids[0]
        task = self.task_manager.get_task(task_id)
        
        if task:
            dialog = LogViewDialog(self, task.name)
            dialog.exec()

class TaskEditDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.setWindowTitle("编辑任务" if task else "新增任务")
        self.setMinimumSize(500, 450)
        
        self.task = task
        
        self.init_ui()
        apply_stylesheet(self)
        
        if task:
            self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 任务名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("任务名称:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入任务名称")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 业务类型
        business_layout = QHBoxLayout()
        business_layout.addWidget(QLabel("业务类型:"))
        self.business_combo = QComboBox()
        businesses = get_all_businesses()
        for b in businesses:
            self.business_combo.addItem(b.get_display_name(), b.get_name())
        business_layout.addWidget(self.business_combo)
        layout.addLayout(business_layout)
        
        # 调度方式
        schedule_group = QGroupBox("调度方式")
        schedule_layout = QVBoxLayout(schedule_group)
        
        self.interval_radio = QCheckBox("间隔执行")
        self.interval_radio.toggled.connect(self._update_schedule_ui)
        schedule_layout.addWidget(self.interval_radio)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("间隔时间(秒):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(10)
        self.interval_spin.setMaximum(86400)
        self.interval_spin.setValue(300)
        interval_layout.addWidget(self.interval_spin)
        schedule_layout.addLayout(interval_layout)
        
        self.fixed_radio = QCheckBox("固定时间")
        self.fixed_radio.toggled.connect(self._update_schedule_ui)
        schedule_layout.addWidget(self.fixed_radio)
        
        fixed_layout = QHBoxLayout()
        fixed_layout.addWidget(QLabel("执行时间:"))
        self.fixed_edit = QLineEdit()
        self.fixed_edit.setPlaceholderText("HH:MM")
        fixed_layout.addWidget(self.fixed_edit)
        schedule_layout.addLayout(fixed_layout)
        
        self.cron_radio = QCheckBox("Cron表达式")
        self.cron_radio.toggled.connect(self._update_schedule_ui)
        schedule_layout.addWidget(self.cron_radio)
        
        cron_layout = QHBoxLayout()
        cron_layout.addWidget(QLabel("Cron表达式:"))
        self.cron_edit = QLineEdit()
        self.cron_edit.setPlaceholderText("分 时 日 月 周")
        cron_layout.addWidget(self.cron_edit)
        schedule_layout.addLayout(cron_layout)
        
        layout.addWidget(schedule_group)
        
        # 关联账号
        account_layout = QHBoxLayout()
        account_layout.addWidget(QLabel("关联账号:"))
        self.account_combo = QComboBox()
        self.account_combo.addItem("无", None)
        accounts = AccountManager().get_all_accounts()
        for acc in accounts:
            self.account_combo.addItem(acc.name, acc.id)
        account_layout.addWidget(self.account_combo)
        layout.addLayout(account_layout)
        
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
        
        self.interval_radio.setChecked(True)
        self._update_schedule_ui()
    
    def _update_schedule_ui(self):
        """更新调度方式UI"""
        self.interval_spin.setEnabled(self.interval_radio.isChecked())
        self.fixed_edit.setEnabled(self.fixed_radio.isChecked())
        self.cron_edit.setEnabled(self.cron_radio.isChecked())
    
    def load_data(self):
        """加载任务数据"""
        if self.task:
            self.name_edit.setText(self.task.name)
            self.business_combo.setCurrentIndex(self.business_combo.findData(self.task.business_name))
            
            if self.task.schedule_type == 'interval':
                self.interval_radio.setChecked(True)
                self.interval_spin.setValue(self.task.interval_seconds)
            elif self.task.schedule_type == 'fixed_time':
                self.fixed_radio.setChecked(True)
                self.fixed_edit.setText(self.task.fixed_time)
            elif self.task.schedule_type == 'cron':
                self.cron_radio.setChecked(True)
                self.cron_edit.setText(self.task.cron_expression)
            
            self.account_combo.setCurrentIndex(self.account_combo.findData(self.task.account_id))
    
    def get_data(self):
        """获取表单数据"""
        schedule_type = 'interval'
        interval_seconds = 300
        fixed_time = None
        cron_expression = None
        
        if self.interval_radio.isChecked():
            schedule_type = 'interval'
            interval_seconds = self.interval_spin.value()
        elif self.fixed_radio.isChecked():
            schedule_type = 'fixed_time'
            fixed_time = self.fixed_edit.text()
        elif self.cron_radio.isChecked():
            schedule_type = 'cron'
            cron_expression = self.cron_edit.text()
        
        return {
            'name': self.name_edit.text(),
            'business_name': self.business_combo.currentData(),
            'schedule_type': schedule_type,
            'interval_seconds': interval_seconds,
            'fixed_time': fixed_time,
            'cron_expression': cron_expression,
            'account_id': self.account_combo.currentData(),
            'params': {}
        }
    
    def accept(self):
        """验证并确认"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入任务名称")
            return
        
        if self.fixed_radio.isChecked() and not self.fixed_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入执行时间")
            return
        
        if self.cron_radio.isChecked() and not self.cron_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入Cron表达式")
            return
        
        super().accept()

class LogViewDialog(QDialog):
    def __init__(self, parent=None, task_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"任务日志 - {task_name}")
        self.setMinimumSize(800, 500)
        
        self.task_name = task_name
        
        self.init_ui()
        apply_stylesheet(self)
        
        self.load_logs()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_logs)
        self.timer.start(2000)
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_logs)
        button_layout.addWidget(self.refresh_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setObjectName("secondaryBtn")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_logs(self):
        """加载日志"""
        log_path = f"logs/office_assistant_{self._get_today_date()}.log"
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.setText(content)
                    self.log_text.moveCursor(self.log_text.textCursor().End)
            except Exception as e:
                logger.error(f"读取日志失败: {e}")
    
    def _get_today_date(self):
        """获取今天日期字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d")
    
    def reject(self):
        """关闭对话框"""
        self.timer.stop()
        super().reject()
