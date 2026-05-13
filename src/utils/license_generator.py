#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证生成器 - 用于生成正式许可证
"""

import os
import sys
import json
import base64
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes, hmac

# 加密密钥（必须与许可证管理器中的密钥一致）
ENCRYPTION_KEY = b'0123456789ABCDEF0123456789ABCDEF'  # 32 bytes for AES-256
HMAC_KEY = b'FEDCBA9876543210FEDCBA9876543210'  # 32 bytes for HMAC


class LicenseGenerator:
    """许可证生成器"""
    
    @staticmethod
    def _pad(data):
        """PKCS7 填充"""
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data
    
    @staticmethod
    def _unpad(data):
        """PKCS7 去填充"""
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(data) + unpadder.finalize()
        return unpadded_data
    
    @staticmethod
    def _encrypt(plaintext):
        """AES-256-CBC 加密"""
        iv = os.urandom(16)  # 16 bytes IV
        cipher = Cipher(algorithms.AES(ENCRYPTION_KEY), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        padded_data = LicenseGenerator._pad(plaintext.encode('utf-8'))
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # 计算 HMAC
        h = hmac.HMAC(HMAC_KEY, hashes.SHA256(), backend=default_backend())
        h.update(iv + ciphertext)
        signature = h.finalize()
        
        # 返回: IV + 签名 + 密文 (Base64编码)
        return base64.b64encode(iv + signature + ciphertext).decode('utf-8')
    
    @staticmethod
    def generate_license(machine_fingerprint, username, start_date=None, days=365):
        """
        生成许可证
        
        :param machine_fingerprint: 机器指纹
        :param username: 用户名
        :param start_date: 开始日期 (datetime对象，默认为当前时间)
        :param days: 有效期天数 (默认365天)
        :return: 加密的许可证字符串
        """
        if start_date is None:
            start_date = datetime.now()
        
        end_date = start_date + timedelta(days=days)
        
        license_data = {
            'type': '正式版',
            'username': username,
            'fingerprint': machine_fingerprint,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'activated': True,
            'version': '1.0',
            'issued_date': datetime.now().isoformat()
        }
        
        json_data = json.dumps(license_data, indent=2, ensure_ascii=False)
        encrypted_license = LicenseGenerator._encrypt(json_data)
        
        return encrypted_license
    
    @staticmethod
    def verify_license(license_code):
        """验证许可证内容（解密查看）"""
        try:
            data = base64.b64decode(license_code)
            
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
            
            json_data = LicenseGenerator._unpad(padded_data).decode('utf-8')
            return json.loads(json_data)
            
        except Exception as e:
            print(f"验证失败: {e}")
            return None


# 命令行工具
def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='许可证生成器')
    parser.add_argument('--fingerprint', '-f', required=True, help='机器指纹')
    parser.add_argument('--username', '-u', required=True, help='用户名')
    parser.add_argument('--days', '-d', type=int, default=365, help='有效期天数')
    parser.add_argument('--output', '-o', help='输出文件')
    
    args = parser.parse_args()
    
    print(f"生成许可证:")
    print(f"  机器指纹: {args.fingerprint}")
    print(f"  用户名: {args.username}")
    print(f"  有效期: {args.days} 天")
    print()
    
    license_code = LicenseGenerator.generate_license(
        machine_fingerprint=args.fingerprint,
        username=args.username,
        days=args.days
    )
    
    print(f"激活码:\n{license_code}")
    print()
    
    # 验证生成的许可证
    decoded = LicenseGenerator.verify_license(license_code)
    if decoded:
        print(f"验证成功:")
        print(f"  类型: {decoded.get('type')}")
        print(f"  用户: {decoded.get('username')}")
        print(f"  到期: {decoded.get('end_date')}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(license_code)
        print(f"\n许可证已保存到: {args.output}")


if __name__ == "__main__":
    main()
