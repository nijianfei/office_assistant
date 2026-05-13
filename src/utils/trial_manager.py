#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试用管理器 - 完善的离线试用机制
特点：
1. 硬件指纹幂等生成
2. 多位置加密存储
3. 时间回滚检测
4. 累计运行时长限制
5. 完全离线运行
"""

import os
import json
import hashlib
import base64
import platform
import psutil
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes, hmac
from src.utils.logger import logger

# 加密密钥（从硬件信息派生，确保同一设备密钥相同）
SEED_KEY = b'OfficeAssistant2024!@#'  # 基础密钥

# 试用时长配置
TRIAL_DAYS = 90
MAX_RUN_HOURS = 90 * 8  # 假设每天使用8小时

# 多重存储位置 - 按优先级排序，从最容易访问到最难访问
STORAGE_PATHS = [
    # 项目根目录（最优先）
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'trial.dat'),
    # 项目 data 目录
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'trial.dat'),
    # 用户目录下的隐藏文件夹（需要创建）
    os.path.join(os.path.expanduser('~'), '.office_assistant', 'trial.dat'),
    # Windows AppData 目录
    os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'OfficeAssistant', 'trial.dat'),
]


class HardwareFingerprint:
    """硬件指纹生成器 - 确保幂等性"""
    
    @staticmethod
    def _get_cpu_info():
        """获取CPU信息"""
        try:
            if platform.system() == 'Windows':
                return platform.processor() or "unknown_cpu"
            else:
                import subprocess
                return subprocess.check_output(['cat', '/proc/cpuinfo']).decode('utf-8')[:200]
        except:
            return "unknown_cpu"
    
    @staticmethod
    def _get_mac_address():
        """获取MAC地址"""
        try:
            interfaces = psutil.net_if_addrs()
            for name, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK and addr.address and ':' in addr.address:
                        return addr.address
            return "unknown_mac"
        except:
            return "unknown_mac"
    
    @staticmethod
    def _get_disk_serial():
        """获取磁盘序列号"""
        try:
            if platform.system() == 'Windows':
                import subprocess
                result = subprocess.check_output(['wmic', 'logicaldisk', 'get', 'name,volumeSerialNumber'], text=True)
                lines = result.strip().split('\n')
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
                return "unknown_disk"
            else:
                import subprocess
                return subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', '/dev/sda1']).decode('utf-8').strip()
        except:
            return "unknown_disk"
    
    @staticmethod
    def _get_bios_uuid():
        """获取BIOS UUID"""
        try:
            if platform.system() == 'Windows':
                import subprocess
                result = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID'], text=True)
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            else:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    return f.read().strip()
            return "unknown_uuid"
        except:
            return "unknown_uuid"
    
    @staticmethod
    def generate_fingerprint():
        """生成唯一的机器指纹（幂等）"""
        cpu_info = HardwareFingerprint._get_cpu_info()
        mac_addr = HardwareFingerprint._get_mac_address()
        disk_serial = HardwareFingerprint._get_disk_serial()
        bios_uuid = HardwareFingerprint._get_bios_uuid()
        
        # 组合所有信息并生成哈希
        raw = f"{cpu_info}|{mac_addr}|{disk_serial}|{bios_uuid}"
        fingerprint = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        
        logger.debug(f"生成机器指纹: {fingerprint[:16]}...")
        return fingerprint
    
    @staticmethod
    def derive_key(fingerprint):
        """从指纹派生加密密钥（确保同一设备密钥相同）"""
        return hashlib.sha256(SEED_KEY + fingerprint.encode('utf-8')).digest()


class TrialManager:
    """试用管理器"""
    
    def __init__(self):
        self.fingerprint = HardwareFingerprint.generate_fingerprint()
        self.encryption_key = HardwareFingerprint.derive_key(self.fingerprint)
        self.hmac_key = hashlib.sha256(b'HMAC' + self.encryption_key).digest()
        self.trial_data = self._load_trial_data()
    
    def _pad(self, data):
        """PKCS7 填充"""
        padder = padding.PKCS7(128).padder()
        return padder.update(data) + padder.finalize()
    
    def _unpad(self, data):
        """PKCS7 去填充"""
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(data) + unpadder.finalize()
    
    def _encrypt(self, plaintext):
        """AES-256-CBC 加密"""
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padded_data = self._pad(plaintext.encode('utf-8'))
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 计算 HMAC
        h = hmac.HMAC(self.hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(iv + ciphertext)
        signature = h.finalize()
        
        return base64.b64encode(iv + signature + ciphertext).decode('utf-8')
    
    def _decrypt(self, encrypted_data):
        """AES-256-CBC 解密"""
        try:
            import base64
            data = base64.b64decode(encrypted_data)
            
            iv = data[:16]
            signature = data[16:48]
            ciphertext = data[48:]
            
            # 验证 HMAC
            h = hmac.HMAC(self.hmac_key, hashes.SHA256(), backend=default_backend())
            h.update(iv + ciphertext)
            h.verify(signature)
            
            # 解密
            cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return self._unpad(padded_data).decode('utf-8')
        
        except Exception as e:
            logger.error(f"解密失败: {e}")
            return None
    
    def _load_from_path(self, path):
        """从指定路径加载试用数据"""
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    encrypted_content = f.read().strip()
                
                if encrypted_content:
                    decrypted = self._decrypt(encrypted_content)
                    if decrypted:
                        return json.loads(decrypted)
            except Exception as e:
                logger.warning(f"从 {path} 加载失败: {e}")
        return None
    
    def _save_to_path(self, path, data):
        """保存试用数据到指定路径"""
        # 跳过空路径
        if not path or not path.strip():
            return False
            
        try:
            # 确保目录存在
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # 检查路径是否可写
            if dir_path and not os.access(dir_path, os.W_OK):
                logger.debug(f"路径不可写: {dir_path}")
                return False
            
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            encrypted_data = self._encrypt(json_data)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            logger.debug(f"成功保存试用数据到: {path}")
            return True
        except PermissionError:
            logger.debug(f"权限不足，跳过保存到: {path}")
            return False
        except Exception as e:
            logger.debug(f"保存到 {path} 失败: {e}")
            return False
    
    def _load_trial_data(self):
        """从多个位置加载试用数据（取最新的有效数据）"""
        all_data = []
        
        for path in STORAGE_PATHS:
            data = self._load_from_path(path)
            if data:
                all_data.append((path, data))
        
        if not all_data:
            # 首次运行，创建新的试用数据
            return self._create_new_trial()
        
        # 选择最后运行时间最大的数据（防止回滚）
        all_data.sort(key=lambda x: x[1].get('last_run_time', 0), reverse=True)
        best_data = all_data[0][1]
        
        # 同步到所有位置
        for path, _ in all_data:
            self._save_to_path(path, best_data)
        
        return best_data
    
    def _create_new_trial(self):
        """创建新的试用数据"""
        now = datetime.now()
        trial_data = {
            'fingerprint': self.fingerprint,
            'first_start_time': now.isoformat(),
            'last_run_time': now.isoformat(),
            'max_time_record': now.timestamp(),
            'total_run_seconds': 0,
            'startup_count': 1,
            'version': '1.0'
        }
        
        # 保存到所有位置
        for path in STORAGE_PATHS:
            self._save_to_path(path, trial_data)
        
        logger.info(f"首次启动，创建试用数据: {now}")
        return trial_data
    
    def _update_trial_data(self):
        """更新试用数据"""
        now = datetime.now()
        now_timestamp = now.timestamp()
        
        # 更新数据
        self.trial_data['last_run_time'] = now.isoformat()
        self.trial_data['max_time_record'] = max(self.trial_data.get('max_time_record', 0), now_timestamp)
        self.trial_data['startup_count'] = self.trial_data.get('startup_count', 0) + 1
        
        # 保存到所有位置
        for path in STORAGE_PATHS:
            self._save_to_path(path, self.trial_data)
    
    def _check_time_rollback(self):
        """检查时间回滚"""
        now = datetime.now()
        now_timestamp = now.timestamp()
        max_record = self.trial_data.get('max_time_record', 0)
        
        # 当前时间小于历史最大时间 → 时间回滚
        if now_timestamp < max_record:
            time_diff = max_record - now_timestamp
            # 允许5分钟误差
            if time_diff > 300:
                logger.error(f"检测到时间回滚: 当前时间 {now} < 历史最大时间 {datetime.fromtimestamp(max_record)}")
                return True
        return False
    
    def _check_time_jump(self):
        """检查时间大幅跳变"""
        last_run = self.trial_data.get('last_run_time')
        if not last_run:
            return False
        
        try:
            last_timestamp = datetime.fromisoformat(last_run).timestamp()
            now_timestamp = datetime.now().timestamp()
            time_diff = now_timestamp - last_timestamp
            
            # 如果时间向前跳变超过24小时，视为异常
            if time_diff > 86400:  # 24小时
                logger.error(f"检测到时间大幅跳变: 上次运行 {last_run}, 当前时间 {datetime.now()}")
                return True
        except Exception as e:
            logger.error(f"检查时间跳变失败: {e}")
        
        return False
    
    def _calculate_remaining_days(self):
        """计算剩余试用天数"""
        first_start = self.trial_data.get('first_start_time')
        if not first_start:
            return TRIAL_DAYS
        
        try:
            first_date = datetime.fromisoformat(first_start)
            end_date = first_date + timedelta(days=TRIAL_DAYS)
            remaining = (end_date - datetime.now()).days
            return max(0, remaining)
        except Exception as e:
            logger.error(f"计算剩余天数失败: {e}")
            return 0
    
    def _calculate_remaining_hours(self):
        """计算剩余运行时长"""
        total_seconds = self.trial_data.get('total_run_seconds', 0)
        remaining_seconds = MAX_RUN_HOURS * 3600 - total_seconds
        return max(0, remaining_seconds / 3600)
    
    def is_trial_valid(self):
        """检查试用是否有效"""
        # 1. 检查时间回滚
        if self._check_time_rollback():
            logger.error("试用过期: 检测到时间回滚")
            return False
        
        # 2. 检查时间跳变
        if self._check_time_jump():
            logger.error("试用过期: 检测到时间大幅跳变")
            return False
        
        # 3. 检查天数限制
        remaining_days = self._calculate_remaining_days()
        if remaining_days <= 0:
            logger.error(f"试用过期: 已超过 {TRIAL_DAYS} 天")
            return False
        
        # 4. 检查累计运行时长限制
        remaining_hours = self._calculate_remaining_hours()
        if remaining_hours <= 0:
            logger.error(f"试用过期: 累计运行时长已超过 {MAX_RUN_HOURS} 小时")
            return False
        
        # 5. 更新试用数据
        self._update_trial_data()
        
        return True
    
    def get_trial_info(self):
        """获取试用信息"""
        return {
            'fingerprint': self.fingerprint[:16] + '...',
            'first_start_time': self.trial_data.get('first_start_time'),
            'last_run_time': self.trial_data.get('last_run_time'),
            'remaining_days': self._calculate_remaining_days(),
            'remaining_hours': round(self._calculate_remaining_hours(), 2),
            'total_run_hours': round(self.trial_data.get('total_run_seconds', 0) / 3600, 2),
            'startup_count': self.trial_data.get('startup_count', 0),
            'is_valid': self.is_trial_valid()
        }
    
    def update_run_duration(self, duration_seconds):
        """更新累计运行时长"""
        self.trial_data['total_run_seconds'] = self.trial_data.get('total_run_seconds', 0) + duration_seconds
        for path in STORAGE_PATHS:
            self._save_to_path(path, self.trial_data)


if __name__ == "__main__":
    # 测试
    tm = TrialManager()
    info = tm.get_trial_info()
    
    print("=== 试用管理器测试 ===")
    print(f"机器指纹: {info['fingerprint']}")
    print(f"首次启动: {info['first_start_time']}")
    print(f"上次运行: {info['last_run_time']}")
    print(f"剩余天数: {info['remaining_days']}")
    print(f"剩余时长: {info['remaining_hours']} 小时")
    print(f"累计运行: {info['total_run_hours']} 小时")
    print(f"启动次数: {info['startup_count']}")
    print(f"是否有效: {info['is_valid']}")
