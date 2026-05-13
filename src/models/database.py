#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块 - 使用 SQLAlchemy
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from src.utils.logger import logger

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    url = Column(Text)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    business_name = Column(String(100), nullable=False)
    schedule_type = Column(String(20), nullable=False)  # interval, fixed_time, cron
    interval_seconds = Column(Integer, default=300)
    fixed_time = Column(String(10))  # HH:MM
    cron_expression = Column(String(100))
    params = Column(JSON, default={})
    account_id = Column(Integer, nullable=True)
    is_enabled = Column(Boolean, default=True)
    status = Column(String(20), default='idle')  # idle, running, success, failed
    last_run_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class DatabaseManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_path = 'data/example_db.sqlite'
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.engine = create_engine(f'sqlite:///{self.db_path}', connect_args={'check_same_thread': False})
        self.Session = sessionmaker(bind=self.engine)
        self._initialized = True
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("数据库表初始化完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
