#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self, name='office_assistant', log_dir='logs/', level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(console_formatter)
        self.logger.addHandler(file_handler)
    
    def get_logger(self):
        return self.logger

# 创建全局日志实例
logger = Logger().get_logger()
