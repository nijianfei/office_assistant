#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理模块
"""

from datetime import datetime
from src.models.database import DatabaseManager, Task
from src.utils.logger import logger

class TaskManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_tasks(self, only_enabled=False):
        """获取所有任务"""
        session = self.db.get_session()
        try:
            query = session.query(Task)
            if only_enabled:
                query = query.filter(Task.is_enabled == True)
            return query.all()
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            return []
        finally:
            session.close()
    
    def get_task(self, task_id):
        """获取单个任务"""
        session = self.db.get_session()
        try:
            return session.query(Task).filter(Task.id == task_id).first()
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            return None
        finally:
            session.close()
    
    def add_task(self, name, business_name, schedule_type, **kwargs):
        """添加任务"""
        session = self.db.get_session()
        try:
            task = Task(
                name=name,
                business_name=business_name,
                schedule_type=schedule_type,
                interval_seconds=kwargs.get('interval_seconds', 300),
                fixed_time=kwargs.get('fixed_time'),
                cron_expression=kwargs.get('cron_expression'),
                params=kwargs.get('params', {}),
                account_id=kwargs.get('account_id'),
                is_enabled=kwargs.get('is_enabled', True),
                status='idle',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(task)
            session.commit()
            logger.info(f"添加任务成功: {name}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"添加任务失败: {e}")
            return None
        finally:
            session.close()
    
    def update_task(self, task_id, **kwargs):
        """更新任务"""
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
            
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            session.commit()
            logger.info(f"更新任务成功: {task_id}")
            return task
        except Exception as e:
            session.rollback()
            logger.error(f"更新任务失败: {e}")
            return None
        finally:
            session.close()
    
    def delete_task(self, task_id):
        """删除任务"""
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                session.delete(task)
                session.commit()
                logger.info(f"删除任务成功: {task_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除任务失败: {e}")
            return False
        finally:
            session.close()
    
    def update_task_status(self, task_id, status):
        """更新任务状态"""
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = status
                if status in ['success', 'failed']:
                    task.last_run_at = datetime.now()
                task.updated_at = datetime.now()
                session.commit()
                logger.info(f"更新任务状态: {task_id} -> {status}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新任务状态失败: {e}")
            return False
        finally:
            session.close()
    
    def toggle_task_enabled(self, task_id):
        """切换任务启用状态"""
        session = self.db.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                task.is_enabled = not task.is_enabled
                task.updated_at = datetime.now()
                session.commit()
                logger.info(f"切换任务状态: {task_id} -> {task.is_enabled}")
                return task.is_enabled
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"切换任务状态失败: {e}")
            return None
