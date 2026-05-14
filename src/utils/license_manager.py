#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证管理器 - 试用版机制（3个月）
支持加密存储，防止篡改
支持机器绑定，防止许可证复制
"""

import os
import json
import base64
import hashlib
import platform
import psutil
import subprocess
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes, hmac
from src.utils.logger import logger

CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

LICENSE_FILE = 'data/license.dat'  # 更改扩展名
TRIAL_DAYS = 90

# 加密密钥（使用固定密钥，可以考虑从环境变量或硬件信息生成）
# 注意：在实际生产环境中，应该使用更安全的密钥管理方式
ENCRYPTION_KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes for AES-256
HMAC_KEY = b'FEDCBA9876543210FEDCBA9876543210'  # 32 bytes for HMAC


class HardwareFingerprint:
    """硬件指纹生成器"""
    
    @staticmethod
    def get_cpu_info():
        """获取CPU信息"""
        try:
            if platform.system() == 'Windows':
                return platform.processor()
            else:
                return subprocess.check_output(['cat', '/proc/cpuinfo'], creationflags=CREATE_NO_WINDOW).decode('utf-8')[:100]
        except Exception as e:
            logger.warning(f"获取CPU信息失败: {e}")
            return "unknown_cpu"
    
    @staticmethod
    def get_mac_address():
        """获取MAC地址"""
        try:
            interfaces = psutil.net_if_addrs()
            for name, addrs in interfaces.items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK and addr.address and ':' in addr.address:
                        return addr.address
            return "unknown_mac"
        except Exception as e:
            logger.warning(f"获取MAC地址失败: {e}")
            return "unknown_mac"
    
    @staticmethod
    def get_disk_serial():
        """获取磁盘序列号"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.check_output(['wmic', 'logicaldisk', 'get', 'name,volumeSerialNumber'], text=True, creationflags=CREATE_NO_WINDOW)
                lines = result.strip().split('\n')
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == 'C:':
                        return parts[1]
                # 如果 C 盘没有找到，返回第一个磁盘的序列号
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]
                return "unknown_disk"
            else:
                return subprocess.check_output(['blkid', '-s', 'UUID', '-o', 'value', '/dev/sda1'], creationflags=CREATE_NO_WINDOW).decode('utf-8').strip()
        except Exception as e:
            logger.warning(f"获取磁盘序列号失败: {e}")
            return "unknown_disk"
    
    @staticmethod
    def get_bios_uuid():
        """获取BIOS UUID"""
        try:
            if platform.system() == 'Windows':
                result = subprocess.check_output(['wmic', 'csproduct', 'get', 'UUID'], text=True, creationflags=CREATE_NO_WINDOW)
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
            else:
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    return f.read().strip()
            return "unknown_uuid"
        except Exception as e:
            logger.warning(f"获取BIOS UUID失败: {e}")
            return "unknown_uuid"
    
    @staticmethod
    def generate_fingerprint():
        """生成唯一的机器指纹"""
        # 收集多种硬件信息
        cpu_info = HardwareFingerprint.get_cpu_info()
        mac_addr = HardwareFingerprint.get_mac_address()
        disk_serial = HardwareFingerprint.get_disk_serial()
        bios_uuid = HardwareFingerprint.get_bios_uuid()
        
        # 组合所有信息并生成哈希
        raw_fingerprint = f"{cpu_info}|{mac_addr}|{disk_serial}|{bios_uuid}"
        fingerprint = hashlib.sha256(raw_fingerprint.encode('utf-8')).hexdigest()
        
        logger.debug(f"生成机器指纹: {fingerprint[:16]}...")
        return fingerprint


class LicenseManager:
    def __init__(self):
        self.machine_fingerprint = HardwareFingerprint.generate_fingerprint()
        self.license_data = self._load_license()
    
    def _pad(self, data):
        """PKCS7 填充"""
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data
    
    def _unpad(self, data):
        """PKCS7 去填充"""
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(data) + unpadder.finalize()
        return unpadded_data
    
    def _encrypt(self, plaintext):
        """AES-256-CBC 加密"""
        iv = os.urandom(16)  # 16 bytes IV
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padded_data = self._pad(plaintext.encode('utf-8'))
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 计算 HMAC
        h = hmac.HMAC(HMAC_KEY, hashes.SHA256(), backend=default_backend())
        h.update(iv + ciphertext)
        signature = h.finalize()
        
        # 返回: IV + 签名 + 密文
        return base64.b64encode(iv + signature + ciphertext).decode('utf-8')
    
    def _decrypt(self, encrypted_data):
        """AES-256-CBC 解密"""
        try:
            data = base64.b64decode(encrypted_data)
            
            # 解析: IV(16) + 签名(32) + 密文
            iv = data[:16]
            signature = data[16:48]
            ciphertext = data[48:]
            
            # 验证 HMAC
            h = hmac.HMAC(HMAC_KEY, hashes.SHA256(), backend=default_backend())
            h.update(iv + ciphertext)
            h.verify(signature)
            
            # 解密
            cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            return self._unpad(padded_data).decode('utf-8')
        
        except Exception as e:
            logger.error(f"解密许可证失败: {e}")
            return None
    
    def _load_license(self):
        """加载许可证文件（加密）"""
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r', encoding='utf-8') as f:
                    encrypted_content = f.read().strip()
                
                # 如果文件为空，视为无效
                if not encrypted_content:
                    logger.error("许可证文件为空！")
                    return self._create_invalid_license()
                
                decrypted_content = self._decrypt(encrypted_content)
                if decrypted_content:
                    license_data = json.loads(decrypted_content)
                    
                    # 验证机器绑定
                    if 'fingerprint' in license_data:
                        if license_data['fingerprint'] != self.machine_fingerprint:
                            logger.error("许可证与当前机器不匹配！")
                            return self._create_invalid_license()
                    
                    return license_data
                else:
                    # 解密失败，视为无效许可证（文件存在但内容损坏）
                    logger.error("许可证解密失败，文件可能已损坏或被篡改！")
                    return self._create_invalid_license()
                
            except Exception as e:
                logger.error(f"加载许可证文件失败: {e}")
                return self._create_invalid_license()
        
        # 如果没有许可证文件（首次启动），也视为无效，需要激活
        logger.info("许可证文件不存在，需要激活")
        return self._create_invalid_license()
    
    def _create_invalid_license(self):
        """创建无效许可证标记（用于文件存在但解密失败的情况）"""
        return {
            'type': 'invalid',
            'valid': False,
            'message': '许可证无效或已损坏'
        }
    
    def _create_trial_license(self):
        """创建试用许可证（绑定当前机器）"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=TRIAL_DAYS)
        
        license_data = {
            'type': 'trial',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'activated': True,
            'remaining_days': TRIAL_DAYS,
            'fingerprint': self.machine_fingerprint,  # 绑定机器指纹
            'version': '1.0'
        }
        
        self._save_license(license_data)
        logger.info(f"创建试用许可证，到期时间: {end_date}")
        return license_data
    
    def _save_license(self, data):
        """保存许可证文件（加密）"""
        try:
            os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            encrypted_data = self._encrypt(json_data)
            
            with open(LICENSE_FILE, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"保存许可证文件失败: {e}")
    
    def is_valid(self):
        """检查许可证是否有效（包括机器绑定验证）"""
        try:
            # 检查是否为无效许可证
            if self.license_data.get('type') == 'invalid':
                logger.error("许可证无效")
                return False
            
            # 检查机器绑定
            if 'fingerprint' in self.license_data:
                if self.license_data['fingerprint'] != self.machine_fingerprint:
                    logger.error("许可证与当前机器不匹配")
                    return False
            
            # 检查有效期
            if 'end_date' not in self.license_data:
                logger.error("许可证缺少到期日期")
                return False
                
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
            'username': self.license_data.get('username', ''),
            'start_date': self.license_data.get('start_date'),
            'end_date': self.license_data.get('end_date'),
            'remaining_days': self.get_remaining_days(),
            'is_valid': self.is_valid(),
            'fingerprint': self.machine_fingerprint[:16] + '...'  # 只显示部分指纹
        }
    
    def get_machine_fingerprint(self):
        """获取当前机器的指纹（用于生成正式许可证）"""
        return self.machine_fingerprint
    
    def validate_license_key(self, license_key):
        """验证激活码（预留接口，用于正式版激活）"""
        # 这里可以实现与服务器验证的逻辑
        # 例如：发送license_key和fingerprint到服务器验证
        logger.info(f"验证激活码: {license_key[:10]}...")
        # 临时返回False，表示未实现正式激活机制
        return False
