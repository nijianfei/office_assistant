#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
许可证生成器测试
"""

import sys
sys.path.insert(0, '.')

from src.utils.license_generator import LicenseGenerator
from src.utils.license_manager import LicenseManager, HardwareFingerprint

print('=== 许可证生成器测试 ===')
print()

# 1. 获取当前机器指纹
fingerprint = HardwareFingerprint.generate_fingerprint()
print(f"当前机器指纹: {fingerprint}")
print()

# 2. 生成许可证
username = "测试用户"
days = 365

print(f"生成许可证:")
print(f"  用户: {username}")
print(f"  有效期: {days} 天")
print()

license_code = LicenseGenerator.generate_license(
    machine_fingerprint=fingerprint,
    username=username,
    days=days
)

print(f"激活码:\n{license_code}")
print()

# 3. 验证许可证内容
print("验证许可证内容:")
decoded = LicenseGenerator.verify_license(license_code)
if decoded:
    print(f"  类型: {decoded.get('type')}")
    print(f"  用户: {decoded.get('username')}")
    print(f"  指纹: {decoded.get('fingerprint')[:16]}...")
    print(f"  开始: {decoded.get('start_date')}")
    print(f"  到期: {decoded.get('end_date')}")
print()

# 4. 保存许可证到文件
license_file = 'data/license.dat'
print(f"保存许可证到: {license_file}")
with open(license_file, 'w', encoding='utf-8') as f:
    f.write(license_code)
print("保存成功!")
print()

# 5. 使用许可证管理器验证
print("使用许可证管理器验证:")
lm = LicenseManager()
info = lm.get_license_info()
print(f"  类型: {info['type']}")
print(f"  用户: {info['username']}")
print(f"  剩余天数: {info['remaining_days']}")
print(f"  是否有效: {info['is_valid']}")
