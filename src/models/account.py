#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号管理模块
"""

from sqlalchemy import or_
from datetime import datetime
from src.models.database import DatabaseManager, Account
from src.utils.logger import logger

class AccountManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_accounts(self, only_enabled=False):
        """获取所有账号"""
        session = self.db.get_session()
        try:
            query = session.query(Account)
            if only_enabled:
                query = query.filter(Account.is_enabled == True)
            return query.all()
        except Exception as e:
            logger.error(f"获取账号列表失败: {e}")
            return []
        finally:
            session.close()
    
    def get_account(self, account_id):
        """获取单个账号"""
        session = self.db.get_session()
        try:
            return session.query(Account).filter(Account.id == account_id).first()
        except Exception as e:
            logger.error(f"获取账号失败: {e}")
            return None
        finally:
            session.close()
    
    def add_account(self, name, username, password, url=None, description=None):
        """添加账号"""
        session = self.db.get_session()
        try:
            account = Account(
                name=name,
                username=username,
                password=password,
                url=url,
                description=description,
                is_enabled=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(account)
            session.commit()
            logger.info(f"添加账号成功: {name}")
            return account
        except Exception as e:
            session.rollback()
            logger.error(f"添加账号失败: {e}")
            return None
        finally:
            session.close()
    
    def update_account(self, account_id, **kwargs):
        """更新账号"""
        session = self.db.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if not account:
                return None
            
            for key, value in kwargs.items():
                if hasattr(account, key):
                    setattr(account, key, value)
            
            account.updated_at = datetime.now()
            session.commit()
            logger.info(f"更新账号成功: {account_id}")
            return account
        except Exception as e:
            session.rollback()
            logger.error(f"更新账号失败: {e}")
            return None
        finally:
            session.close()
    
    def delete_account(self, account_id):
        """删除账号"""
        session = self.db.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                session.delete(account)
                session.commit()
                logger.info(f"删除账号成功: {account_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"删除账号失败: {e}")
            return False
        finally:
            session.close()
    
    def toggle_account_status(self, account_id):
        """切换账号启用状态"""
        session = self.db.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                account.is_enabled = not account.is_enabled
                account.updated_at = datetime.now()
                session.commit()
                logger.info(f"切换账号状态: {account_id} -> {account.is_enabled}")
                return account.is_enabled
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"切换账号状态失败: {e}")
            return None
