#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI样式模块 - 简化版，使用原生Qt样式为主
"""

STYLESHEET = """
/* 仅保留最基础的美化 */

/* 主窗口背景 */
QMainWindow {
    background-color: #f5f5f5;
}

/* 标题标签 */
QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #333;
}

/* 按钮基本样式 */
QPushButton {
    padding: 8px 20px;
    min-width: 80px;
}

/* 危险按钮 */
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: white;
}
"""

def apply_stylesheet(widget):
    """应用样式表 - 简化版本，以原生Qt样式为主"""
    widget.setStyleSheet(STYLESHEET)
