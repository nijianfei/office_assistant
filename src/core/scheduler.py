#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务调度器 - 支持间隔、固定时间、Cron表达式
"""

import threading
from datetime import datetime
from apscheduler.schedulers.qt import QtScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from src.core.browser_manager import BrowserManager
from src.core.business_base import get_business, discover_and_register_businesses
from src.models.task import TaskManager
from src.models.account import AccountManager
from src.utils.logger import logger

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.browser = BrowserManager()
        self.task_manager = TaskManager()
        self.account_manager = AccountManager()
        self.scheduler = QtScheduler()
        self._running = False
        self._job_map = {}  # task_id -> job_id
    
    def start(self):
        """启动调度器"""
        if self._running:
            logger.info("调度器已在运行")
            return
        
        try:
            logger.info("正在启动任务调度器...")
            
            discover_and_register_businesses()
            
            self.scheduler.start()
            self._running = True
            
            self._load_tasks()
            
            logger.info("任务调度器启动成功")
            
        except Exception as e:
            logger.error(f"调度器启动失败: {str(e)}", exc_info=True)
    
    def stop(self):
        """停止调度器"""
        if not self._running:
            return
        
        try:
            logger.info("正在停止任务调度器...")
            
            for job_id in self._job_map.values():
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass
            
            self._job_map.clear()
            self.scheduler.shutdown(wait=False)
            self._running = False
            
            if self.browser.is_alive():
                self.browser.close()
            
            logger.info("任务调度器已停止")
            
        except Exception as e:
            logger.error(f"调度器停止失败: {str(e)}", exc_info=True)
    
    def _load_tasks(self):
        """加载所有已启用的任务"""
        tasks = self.task_manager.get_all_tasks(only_enabled=True)
        logger.info(f"发现 {len(tasks)} 个已启用的任务")
        
        for task in tasks:
            self._schedule_task(task)
    
    def _schedule_task(self, task):
        """调度单个任务"""
        try:
            if task.id in self._job_map:
                self._unschedule_task(task.id)
            
            job_id = f"task_{task.id}"
            trigger = self._create_trigger(task)
            
            if not trigger:
                logger.warning(f"任务 {task.name} 创建调度失败")
                return
            
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                args=[task.id],
                id=job_id,
                name=task.name,
                replace_existing=True
            )
            
            self._job_map[task.id] = job_id
            logger.info(f"任务已调度: {task.name} ({task.schedule_type})")
            
        except Exception as e:
            logger.error(f"调度任务失败 {task.name}: {str(e)}", exc_info=True)
    
    def _unschedule_task(self, task_id):
        """取消任务调度"""
        if task_id not in self._job_map:
            return
        
        try:
            job_id = self._job_map[task_id]
            self.scheduler.remove_job(job_id)
            del self._job_map[task_id]
            logger.info(f"任务已取消调度: {task_id}")
            
        except Exception as e:
            logger.error(f"取消任务调度失败: {e}")
    
    def _create_trigger(self, task):
        """创建任务触发器"""
        if task.schedule_type == 'interval':
            return IntervalTrigger(seconds=task.interval_seconds)
        
        elif task.schedule_type == 'fixed_time':
            if task.fixed_time:
                hour, minute = map(int, task.fixed_time.split(':'))
                return CronTrigger(hour=hour, minute=minute)
        
        elif task.schedule_type == 'cron' and task.cron_expression:
            try:
                parts = task.cron_expression.split()
                if len(parts) >= 5:
                    return CronTrigger(
                        minute=parts[0],
                        hour=parts[1],
                        day=parts[2],
                        month=parts[3],
                        day_of_week=parts[4]
                    )
            except Exception as e:
                logger.warning(f"解析Cron表达式失败: {e}")
        
        return None
    
    def _execute_task(self, task_id):
        """执行任务"""
        task = self.task_manager.get_task(task_id)
        if not task or not task.is_enabled:
            return
        
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行任务: {task.name}")
            logger.info("=" * 60)
            
            self.task_manager.update_task_status(task_id, "running")
            
            if not self.browser.is_alive():
                logger.info("正在初始化浏览器...")
                if not self.browser.initialize(headless=False):
                    logger.error("浏览器初始化失败")
                    self.task_manager.update_task_status(task_id, "failed")
                    return
            
            if task.account_id:
                logger.info(f"关联账号ID: {task.account_id}")
            
            business = get_business(task.business_name)
            if not business:
                logger.error(f"未找到业务逻辑: {task.business_name}")
                self.task_manager.update_task_status(task_id, "failed")
                return
            
            params = task.params or {}
            success = business.execute(self.browser, **params)
            
            if success:
                self.task_manager.update_task_status(task_id, "success")
                logger.info(f"[OK] 任务执行成功: {task.name}")
            else:
                self.task_manager.update_task_status(task_id, "failed")
                logger.error(f"[FAIL] 任务执行失败: {task.name}")
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"执行任务异常 {task.name}: {str(e)}", exc_info=True)
            self.task_manager.update_task_status(task_id, "failed")
    
    def add_task_to_schedule(self, task_id):
        """添加任务到调度"""
        task = self.task_manager.get_task(task_id)
        if task:
            self._schedule_task(task)
    
    def remove_task_from_schedule(self, task_id):
        """从调度中移除任务"""
        self._unschedule_task(task_id)
    
    def run_task_once(self, task_id, wait_complete=True):
        """立即执行一次任务"""
        if wait_complete:
            self._execute_task(task_id)
        else:
            threading.Thread(target=self._execute_task, args=(task_id,), daemon=True).start()
    
    def refresh_task(self, task_id):
        """刷新任务调度"""
        task = self.task_manager.get_task(task_id)
        if task:
            self._unschedule_task(task_id)
            if task.is_enabled:
                self._schedule_task(task)
    
    def is_running(self):
        """调度器是否在运行"""
        return self._running
