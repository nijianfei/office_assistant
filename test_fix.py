#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的代码
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.browser_manager import BrowserManager
from src.business.baidu_test import BaiduTestBusiness
from src.utils.logger import logger

def test_fix():
    """测试修复"""
    print("=" * 60)
    print("测试修复后的百度测试业务")
    print("=" * 60)
    
    # 1. 初始化浏览器
    print("\n1. 初始化浏览器管理器...")
    bm = BrowserManager()
    if not bm.initialize():
        print("[FAIL] 初始化失败")
        return
    
    print("[OK] 初始化成功")
    
    # 2. 创建业务类
    print("\n2. 创建百度测试业务...")
    business = BaiduTestBusiness()
    print(f"   业务名称: {business.get_name()}")
    print(f"   显示名称: {business.get_display_name()}")
    
    # 3. 执行业务
    print("\n3. 执行测试...")
    success = business.execute(bm, search_keyword="办公助手", switch_tabs=True, tab_list="资讯")
    
    print(f"\n4. 执行结果: {'[OK] 成功' if success else '[FAIL] 失败'}")
    
    print("\n5. 按回车键关闭浏览器...")
    input()
    
    print("\n6. 关闭浏览器...")
    bm.close()
    print("[OK] 完成")

if __name__ == "__main__":
    test_fix()
