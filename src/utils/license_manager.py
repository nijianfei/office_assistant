#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证管理器 - 试用版机制（3个月）
"""

import os
import json
from datetime import datetime, timedelta
from src.utils.logger import logger

LICENSE_FILE = 'data/license.json'
TRIAL_DAYS = 90

class LicenseManager:
    def __init__(self):
        self.license_data = self._load_license()
    
    def _load_license(self):
        """加载许可证文件"""
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载许可证文件失败: {e}")
        
        # 如果没有许可证文件，创建新的试用许可证
        return self._create_trial_license()
    
    def _create_trial_license(self):
        """创建试用许可证"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=TRIAL_DAYS)
        
        license_data = {
            'type': 'trial',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'activated': True,
            'remaining_days': TRIAL_DAYS
        }
        
        self._save_license(license_data)
        logger.info(f"创建试用许可证，到期时间: {end_date}")
        return license_data
    
    def _save_license(self, data):
        """保存许可证文件"""
        try:
            os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存许可证文件失败: {e}")
    
    def is_valid(self):
        """检查许可证是否有效"""
        try:
            end_date = datetime.fromisoformat(self.license_data['end_date'])
            return datetime.now() < end_date
        except Exception as e:
            logger.error(f"检查许可证失败: {e}")
            return False
    
    def get_remaining_days(self):
        """获取剩余天数"""
        try:
            end_date = datetime.fromisoformat(self.license_data['end_date'])
            remaining = (end_date - datetime.now()).days
            return max(0, remaining)
        except Exception as e:
            logger.error(f"获取剩余天数失败: {e}")
            return 0
    
    def get_end_date(self):
        """获取到期日期"""
        try:
            return datetime.fromisoformat(self.license_data['end_date'])
        except Exception as e:
            logger.error(f"获取到期日期失败: {e}")
            return None
    
    def get_license_info(self):
        """获取许可证信息"""
        return {
            'type': self.license_data.get('type', 'trial'),
            'start_date': self.license_data.get('start_date'),
            'end_date': self.license_data.get('end_date'),
            'remaining_days': self.get_remaining_days(),
            'is_valid': self.is_valid()
        }
