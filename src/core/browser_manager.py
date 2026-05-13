#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器管理器 - 使用 DrissionPage
参考官方文档：https://drissionpage.cn/browser_control/intro
"""

from DrissionPage import Chromium
from src.utils.logger import logger

class BrowserManager:
    """浏览器管理器"""

    def __init__(self):
        self.browser = None
        self.tab = None
        self._is_initialized = False

    def initialize(self, headless=False):
        """初始化浏览器"""
        try:
            logger.info("正在初始化浏览器...")

            # 使用 Chromium 类启动浏览器
            self.browser = Chromium()
            self.tab = self.browser.latest_tab
            self._is_initialized = True

            logger.info("浏览器初始化成功")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}", exc_info=True)
            return False

    def is_alive(self):
        """检查浏览器是否存活"""
        return self._is_initialized and self.browser is not None

    def get_tab(self):
        """获取当前标签页对象（直接访问 DrissionPage 的 tab）"""
        return self.tab

    def goto(self, url):
        """跳转到指定URL"""
        try:
            logger.info(f"正在跳转: {url}")
            if self.tab:
                self.tab.get(url)
                return True
            return False
        except Exception as e:
            logger.error(f"跳转失败: {e}", exc_info=True)
            return False

    def close(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.quit()
                self.browser = None
                self.tab = None
                self._is_initialized = False
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")

    def wait(self, timeout=30):
        """等待"""
        import time
        time.sleep(timeout)

    def wait_ele(self, selector, timeout=30):
        """等待元素出现"""
        try:
            if self.tab:
                return self.tab.wait.ele_appear(selector, timeout=timeout)
        except Exception:
            return None
        return None

    def ele(self, selector):
        """获取元素"""
        if self.tab:
            return self.tab.ele(selector)
        return None

    def eles(self, selector):
        """获取元素列表"""
        if self.tab:
            return self.tab.eles(selector)
        return []

    def input(self, selector, text):
        """输入文本"""
        try:
            ele = self.ele(selector)
            if ele:
                ele.input(text)
                return True
            return False
        except Exception as e:
            logger.error(f"输入失败: {e}")
            return False

    def click(self, selector):
        """点击元素"""
        try:
            ele = self.ele(selector)
            if ele:
                ele.click()
                return True
            return False
        except Exception as e:
            logger.error(f"点击失败: {e}")
            return False

    def press(self, key):
        """按键"""
        try:
            if self.tab:
                self.tab.ele('').press(key)
        except Exception as e:
            logger.error(f"按键失败: {e}")

    def get_cookies(self):
        """获取cookies"""
        if self.tab:
            return self.tab.cookies()
        return []

    def set_cookies(self, cookies):
        """设置cookies"""
        if self.tab:
            self.tab.set.cookies(cookies)
