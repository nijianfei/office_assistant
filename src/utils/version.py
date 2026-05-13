#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理模块
支持自动版本号更新
"""

import os
import json

# 版本号定义
VERSION_FILE = 'version.json'

# 默认版本配置
DEFAULT_VERSION = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build_number": "001",
    "build_date": "2026-05-13"
}


def _load_version():
    """加载版本信息"""
    if os.path.exists(VERSION_FILE):
        try:
            with open(VERSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载版本文件失败: {e}")
            return DEFAULT_VERSION.copy()
    return DEFAULT_VERSION.copy()


def _save_version(version_data):
    """保存版本信息"""
    try:
        with open(VERSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)
        return True
    except Exception as e:
        print(f"保存版本文件失败: {e}")
        return False


def _get_current_month():
    """获取当前年月字符串 (YYYY-MM)"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m")


def _get_current_date():
    """获取当前日期字符串 (YYYY-MM-DD)"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def increment_build_number():
    """
    自动递增构建编号:
    - 同一年月内 BUILD_NUMBER 累加
    - 不同年月 BUILD_NUMBER 从 001 开始
    """
    version_data = _load_version()
    current_month = _get_current_month()
    
    # 获取上次构建的年月
    last_build_month = version_data.get('build_date', '')[:7]
    
    if last_build_month == current_month:
        # 同月，累加构建编号
        current_num = int(version_data.get('build_number', '001'))
        new_num = current_num + 1
        version_data['build_number'] = f"{new_num:03d}"
    else:
        # 不同月，重置为 001
        version_data['build_number'] = "001"
    
    # 更新构建日期
    version_data['build_date'] = _get_current_date()
    
    if _save_version(version_data):
        print(f"版本号更新: {get_full_version()}")
        return True
    return False


def set_version(major=None, minor=None, patch=None):
    """设置版本号"""
    version_data = _load_version()
    
    if major is not None:
        version_data['major'] = major
    if minor is not None:
        version_data['minor'] = minor
    if patch is not None:
        version_data['patch'] = patch
    
    return _save_version(version_data)


def get_version():
    """获取完整版本号 (X.Y.Z)"""
    version_data = _load_version()
    return f"{version_data['major']}.{version_data['minor']}.{version_data['patch']}"


def get_build_date():
    """获取构建日期"""
    version_data = _load_version()
    return version_data.get('build_date', '')


def get_build_number():
    """获取构建编号"""
    version_data = _load_version()
    return version_data.get('build_number', '001')


def get_full_version():
    """获取完整版本信息（包含版本号、构建日期、构建编号）"""
    return f"{get_version()} (Build {get_build_number()}, {get_build_date()})"


def parse_version(version_str):
    """解析版本号字符串为元组"""
    parts = version_str.split('.')
    return tuple(map(int, parts))


def compare_versions(v1, v2):
    """比较两个版本号"""
    v1_parts = parse_version(v1)
    v2_parts = parse_version(v2)
    
    if v1_parts > v2_parts:
        return 1
    elif v1_parts < v2_parts:
        return -1
    else:
        return 0


# 初始化版本文件
if not os.path.exists(VERSION_FILE):
    _save_version(DEFAULT_VERSION)
    print(f"创建版本文件: {VERSION_FILE}")

if __name__ == "__main__":
    print(f"当前版本: {get_full_version()}")
    print(f"版本号: {get_version()}")
    print(f"构建编号: {get_build_number()}")
    print(f"构建日期: {get_build_date()}")
