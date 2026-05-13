#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浏览器管理器
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('='*60)
print('测试浏览器管理器')
print('='*60)

from src.core.browser_manager import BrowserManager

print('\n[1] 初始化浏览器...')
browser = BrowserManager()
result = browser.initialize(headless=False)
print(f'    结果: {result}')

if not browser.is_alive():
    print('\n[FAIL] 浏览器初始化失败')
    sys.exit(1)

print('\n[2] 访问百度...')
result = browser.goto('https://www.baidu.com')
print(f'    结果: {result}')

browser.wait(2)

print('\n[3] 查找搜索框...')
ele = browser.ele('#kw')
if ele:
    print(f'    [OK] 找到元素: {type(ele)}')
    
    print('\n[4] 输入搜索词...')
    result = browser.input('#kw', '办公助手')
    print(f'    结果: {result}')
    
    browser.wait(1)
    
    print('\n[5] 点击搜索按钮...')
    result = browser.click('#su')
    print(f'    结果: {result}')
    
    browser.wait(3)
    
    print('\n[6] 获取搜索结果...')
    links = browser.eles('tag:h3')
    print(f'    找到 {len(links)} 条结果')
    for i, link in enumerate(links[:3], 1):
        print(f'      [{i}] {link.text}')

print('\n[7] 关闭浏览器...')
browser.close()

print('\n'+'='*60)
print('[OK] 测试完成！')
print('='*60)
