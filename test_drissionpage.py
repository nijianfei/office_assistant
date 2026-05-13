#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrissionPage 完整测试 Demo
参考官方文档：
- https://drissionpage.cn/get_start/installation
- https://drissionpage.cn/browser_control/intro

覆盖功能：
1. 浏览器启动和关闭
2. 访问网页
3. 页面交互（点击、输入）
4. 查找元素（多种选择器）
5. 元素交互（点击、输入、获取信息）
6. iframe 操作
7. 等待机制
8. 截图功能
9. Cookies 操作
10. 标签页管理
11. JavaScript 执行
"""

import sys
import os
import time

print('=' * 70)
print('DrissionPage 完整测试 Demo')
print('参考文档: https://drissionpage.cn')
print('=' * 70)

# -----------------------------------------------------------------------------
# 步骤 1: 导入和版本检查
# -----------------------------------------------------------------------------
print('\n[步骤 1] 导入 DrissionPage 并检查版本')
print('-' * 50)
try:
    from DrissionPage import Chromium, __version__
    print(f'[OK] DrissionPage 导入成功')
    print(f'    版本: {__version__}')
except ImportError as e:
    print(f'[FAIL] 导入失败: {e}')
    print('请安装: pip install DrissionPage')
    sys.exit(1)

# -----------------------------------------------------------------------------
# 步骤 2: 启动浏览器（带配置）
# -----------------------------------------------------------------------------
print('\n[步骤 2] 启动浏览器')
print('-' * 50)
try:
    # 创建浏览器实例（DrissionPage 4.x API）
    browser = Chromium()
    print('[OK] 浏览器启动成功')
    print(f'    浏览器类型: {type(browser).__name__}')
    
    # 可选：设置无头模式（如需）
    # browser.set.headless(True)
    # print('    已设置无头模式')
    
except Exception as e:
    print(f'[FAIL] 启动失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# -----------------------------------------------------------------------------
# 步骤 3: 获取标签页并访问网页
# -----------------------------------------------------------------------------
print('\n[步骤 3] 获取标签页并访问网页')
print('-' * 50)
try:
    tab = browser.latest_tab
    print(f'[OK] 获取标签页成功')
    print(f'    标签页类型: {type(tab).__name__}')
    
    # 访问百度首页
    tab.get('https://www.baidu.com')
    time.sleep(2)
    
    print(f'[OK] 访问成功')
    print(f'    当前URL: {tab.url}')
    print(f'    页面标题: {tab.title}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')
    browser.quit()
    sys.exit(1)

# -----------------------------------------------------------------------------
# 步骤 4: 查找元素（多种选择器）
# -----------------------------------------------------------------------------
print('\n[步骤 4] 查找元素（多种选择器）')
print('-' * 50)
try:
    # 1. CSS选择器
    print('1. CSS选择器:')
    ele_kw = tab.ele('#kw')
    ele_kw.input('DrissionPage 教程 9999')
    print(f'   - #kw (搜索框): {ele_kw is not None}')
    time.sleep(3)

    ele_kw = tab.ele('#chat-textarea')
    ele_kw.input('DrissionPage 教程 88888')
    print(f'   - #chat-textarea (搜索框): {ele_kw is not None}')
    time.sleep(3)

    # 2. XPath
    print('2. XPath选择器:')
    ele_su = tab.ele('xpath://input[@id="su"]')
    print(f'   - xpath://input[@id="su"] (搜索按钮): {ele_su is not None}')
    
    # 3. 文本选择器
    print('3. 文本选择器:')
    ele_text = tab.ele('text:新闻')
    print(f'   - text:新闻: {ele_text is not None}')
    
    # 4. 标签选择器
    print('4. 标签选择器:')
    links = tab.eles('tag:a')
    print(f'   - tag:a (所有链接): 找到 {len(links)} 个')
    
    # 5. 属性选择器
    print('5. 属性选择器:')
    ele_attr = tab.ele('@name=wd')
    print(f'   - @name=wd: {ele_attr is not None}')
    
    # 6. 组合选择器
    print('6. 组合选择器:')
    ele_div = tab.ele('css:.s-top-left a')
    print(f'   - css:.s-top-left a: {ele_div is not None}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 5: 元素交互（输入、点击）
# -----------------------------------------------------------------------------
print('\n[步骤 5] 元素交互（输入、点击）')
print('-' * 50)
try:
    # 输入文本到搜索框
    print('1. 输入文本:')
    ele_kw = tab.ele('#kw')
    ele_kw.input('DrissionPage 教程')
    time.sleep(1)
    print('   [OK] 输入成功')
    
    # 点击搜索按钮（使用JavaScript点击，避免NoRectError）
    print('2. 点击按钮:')
    ele_su = tab.ele('#su')
    ele_su.click(by_js=True)
    time.sleep(3)
    print('   [OK] 点击成功')
    print(f'   当前URL: {tab.url}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 6: 获取元素信息
# -----------------------------------------------------------------------------
print('\n[步骤 6] 获取元素信息')
print('-' * 50)
try:
    # 获取搜索结果
    results = tab.eles('tag:h3')
    print(f'找到 {len(results)} 条搜索结果')
    
    for i, result in enumerate(results[:3], 1):
        print(f'\n{str(i).rjust(2)}. 结果 {i}:')
        print(f'   文本: {result.text}')
        print(f'   标签名: {result.tag}')
        print(f'   是否可见: {result.displayed}')
        print(f'   是否可点击: {result.clickable}')
        
        # 获取属性
        link = result.ele('tag:a')
        if link:
            print(f'   href: {link.attr("href")}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 7: 等待机制
# -----------------------------------------------------------------------------
print('\n[步骤 7] 等待机制')
print('-' * 50)
try:
    # 等待元素出现
    print('1. wait.ele_appear():')
    start_time = time.time()
    ele = tab.wait.ele_appear('#content_left', timeout=10)
    elapsed = time.time() - start_time
    print(f'   等待元素出现耗时: {elapsed:.2f}秒')
    print(f'   结果: {ele is not None}')
    
    # 等待页面加载
    print('2. wait.load_start() / wait.load_end():')
    tab.get('https://www.baidu.com')
    tab.wait.load_start()
    time.sleep(1)
    tab.wait.load_end(timeout=10)
    print('   [OK] 页面加载完成')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 8: JavaScript 执行
# -----------------------------------------------------------------------------
print('\n[步骤 8] JavaScript 执行')
print('-' * 50)
try:
    # 执行简单JS
    result = tab.run_js('return document.title')
    print(f'1. 获取页面标题: {result}')
    
    # 执行复杂JS
    result = tab.run_js('''
        const inputs = document.querySelectorAll('input');
        return inputs.length;
    ''')
    print(f'2. 页面input数量: {result}')
    
    # 修改页面内容
    tab.run_js('document.querySelector("#kw").value = "JS测试"')
    time.sleep(1)
    print('3. 修改页面元素成功')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 9: Cookies 操作
# -----------------------------------------------------------------------------
print('\n[步骤 9] Cookies 操作')
print('-' * 50)
try:
    # 获取所有cookies
    cookies = tab.cookies()
    print(f'1. 获取Cookies: 共 {len(cookies)} 个')
    if cookies:
        print(f'   第一个Cookie: {cookies[0]["name"]}={cookies[0]["value"]}')
    
    # 添加Cookie
    tab.set.cookies({'name': 'test_cookie', 'value': 'hello_drission'})
    print('2. 添加Cookie成功')
    
    # 获取指定Cookie
    cookie = tab.cookie('test_cookie')
    print(f'3. 获取指定Cookie: {cookie}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 10: 标签页管理
# -----------------------------------------------------------------------------
print('\n[步骤 10] 标签页管理')
print('-' * 50)
try:
    # 新建标签页
    new_tab = browser.new_tab('https://www.baidu.com/s?wd=Python')
    time.sleep(2)
    print(f'1. 新建标签页: {new_tab.title}')
    
    # 获取所有标签页
    tabs = browser.tabs()
    print(f'2. 标签页数量: {len(tabs)}')
    
    # 切换标签页
    browser.switch_tab(tab)
    print(f'3. 切换回原标签页: {tab.title}')
    
    # 关闭标签页
    new_tab.close()
    print(f'4. 关闭新建标签页')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 11: 截图功能
# -----------------------------------------------------------------------------
print('\n[步骤 11] 截图功能')
print('-' * 50)
try:
    # 截取整个页面
    screenshot_path = 'screenshot_full.png'
    tab.screenshot(screenshot_path)
    print(f'1. 截取全屏成功: {screenshot_path}')
    
    # 截取元素
    ele_kw = tab.ele('#kw')
    ele_screenshot_path = 'screenshot_elem.png'
    ele_kw.screenshot(ele_screenshot_path)
    print(f'2. 截取元素成功: {ele_screenshot_path}')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 12: 页面信息获取
# -----------------------------------------------------------------------------
print('\n[步骤 12] 页面信息获取')
print('-' * 50)
try:
    print(f'1. URL: {tab.url}')
    print(f'2. 标题: {tab.title}')
    print(f'3. HTML长度: {len(tab.html) // 1000} KB')
    print(f'4. 页面源码(前200字符): {tab.html[:200]}...')
    
except Exception as e:
    print(f'[FAIL] 失败: {e}')

# -----------------------------------------------------------------------------
# 步骤 13: 关闭浏览器
# -----------------------------------------------------------------------------
print('\n[步骤 13] 关闭浏览器')
print('-' * 50)
try:
    browser.quit()
    print('[OK] 浏览器关闭成功')
except Exception as e:
    print(f'[FAIL] 关闭失败: {e}')

print('\n' + '=' * 70)
print('[OK] 所有测试完成！')
print('=' * 70)
print('\n测试覆盖的 DrissionPage 知识点:')
print('  1. 浏览器启动与配置')
print('  2. 标签页管理')
print('  3. 网页访问')
print('  4. 元素定位（CSS/XPath/文本/标签/属性）')
print('  5. 元素交互（输入、点击）')
print('  6. 元素信息获取')
print('  7. 等待机制')
print('  8. JavaScript 执行')
print('  9. Cookies 操作')
print(' 10. 截图功能')
print(' 11. 页面信息获取')
