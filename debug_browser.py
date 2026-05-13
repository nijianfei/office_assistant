#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试浏览器管理器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.browser_manager import BrowserManager
from src.utils.logger import logger

def test_browser_manager():
    """测试浏览器管理器"""
    print("=" * 60)
    print("测试 BrowserManager")
    print("=" * 60)
    
    bm = BrowserManager()
    
    print("\n1. 初始化浏览器...")
    if not bm.initialize():
        print("[FAIL] 初始化失败")
        return
    
    print("[OK] 初始化成功")
    print(f"   browser: {type(bm.browser)}")
    print(f"   tab: {type(bm.tab)}")
    
    print("\n2. 访问百度...")
    bm.goto("https://www.baidu.com")
    print("[OK] 跳转完成")
    bm.wait(3)
    
    print("\n3. 等待搜索框...")
    ele = bm.wait_ele("#kw", timeout=10)
    print(f"   wait_ele 返回: {ele}")
    print(f"   type: {type(ele) if ele else None}")
    
    print("\n4. 直接使用 tab.ele...")
    if bm.tab:
        ele2 = bm.tab.ele("#kw")
        print(f"   tab.ele 返回: {ele2}")
        print(f"   type: {type(ele2) if ele2 else None}")
        print(f"   元素存在: {ele2 is not None}")
        
        if ele2:
            print("\n5. 输入文本...")
            ele2.input("办公助手")
            print("[OK] 输入完成")
            bm.wait(1)
            
            print("\n6. 点击搜索按钮...")
            su_ele = bm.tab.ele("#su")
            if su_ele:
                su_ele.click()
                print("[OK] 点击完成")
                bm.wait(3)
                
                print(f"\n   当前URL: {bm.tab.url}")
                print(f"   页面标题: {bm.tab.title}")
    
    print("\n7. 按回车键继续...")
    input()
    
    print("\n8. 关闭浏览器...")
    bm.close()
    print("[OK] 关闭完成")

if __name__ == "__main__":
    test_browser_manager()
