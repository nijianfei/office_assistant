#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度测试业务
演示登录、搜索、标签切换等功能
"""

from typing import Dict, Any
from src.core.business_base import BaseBusiness
from src.utils.logger import logger

class BaiduTestBusiness(BaseBusiness):
    """百度测试业务"""

    def get_name(self) -> str:
        return "baidu_test"

    def get_display_name(self) -> str:
        return "百度测试"

    def get_description(self) -> str:
        return "百度网站自动化测试：搜索、标签切换、结果遍历"

    def get_param_schema(self) -> Dict[str, Any]:
        return {
            "search_keyword": {
                "type": "string",
                "label": "搜索关键词",
                "default": "办公助手",
                "required": True
            },
            "switch_tabs": {
                "type": "boolean",
                "label": "切换搜索标签",
                "default": True,
                "required": False
            },
            "tab_list": {
                "type": "select",
                "label": "要切换的标签",
                "default": "资讯",
                "options": ["资讯", "视频", "图片", "贴吧", "文库"],
                "required": False
            },
            "result_count": {
                "type": "number",
                "label": "遍历结果数",
                "default": 3,
                "required": False
            }
        }

    def execute(self, browser, **kwargs) -> bool:
        """执行百度测试业务"""
        try:
            search_keyword = kwargs.get("search_keyword", "办公助手")
            switch_tabs = kwargs.get("switch_tabs", True)
            tab_type = kwargs.get("tab_list", "资讯")
            result_count = kwargs.get("result_count", 3)

            # 获取原生的 DrissionPage tab 对象
            tab = browser.get_tab()
            if not tab:
                logger.error("无法获取浏览器标签页")
                return False

            logger.info("=" * 50)
            logger.info(f"开始执行百度测试: {search_keyword}")
            logger.info("=" * 50)

            # 1. 打开百度首页
            logger.info("[1/6] 正在打开百度首页...")
            tab.get("https://www.baidu.com")
            browser.wait(2)
            logger.info("[OK] 百度首页打开成功")

            # 2. 输入搜索关键词
            logger.info(f"[2/6] 正在输入搜索词: {search_keyword}")
            try:
                kw_ele = tab.ele("#kw", timeout=10)
                if kw_ele:
                    kw_ele.input(search_keyword)
                    browser.wait(1)
                    logger.info("[OK] 搜索词输入成功")
                else:
                    logger.error("未找到搜索框元素 #kw")
                    return False
            except Exception as e:
                logger.error(f"输入搜索词失败: {e}", exc_info=True)
                return False

            # 3. 点击搜索按钮
            logger.info("[3/6] 正在点击搜索按钮...")
            try:
                su_ele = tab.ele("#su", timeout=10)
                if su_ele:
                    # 使用 JavaScript 点击，避免 NoRectError
                    su_ele.click(by_js=True)
                    browser.wait(3)
                    logger.info("[OK] 搜索按钮点击成功")
                else:
                    logger.error("未找到搜索按钮元素 #su")
                    return False
            except Exception as e:
                logger.error(f"点击搜索按钮失败: {e}", exc_info=True)
                # 尝试备用方案：按回车键
                try:
                    logger.info("尝试备用方案：按回车键搜索")
                    kw_ele = tab.ele("#kw")
                    if kw_ele:
                        kw_ele.press("Enter")
                        browser.wait(3)
                        logger.info("[OK] 回车搜索成功")
                    else:
                        return False
                except Exception as e2:
                    logger.error(f"备用方案也失败: {e2}", exc_info=True)
                    return False

            # 4. 等待结果加载
            logger.info("[4/6] 正在等待搜索结果...")
            try:
                content_ele = tab.ele("#content_left", timeout=15)
                if content_ele:
                    browser.wait(2)
                    logger.info("[OK] 搜索结果加载完成")

                    # 遍历搜索结果
                    results = tab.eles("tag:h3")
                    logger.info(f"找到 {len(results)} 条搜索结果")

                    for i, result in enumerate(results[:result_count], 1):
                        try:
                            title = result.text
                            logger.info(f"  [{i}] {title}")
                        except Exception as e:
                            logger.warning(f"获取结果 {i} 信息失败: {e}")
                else:
                    logger.warning("未找到搜索结果区域 #content_left")

            except Exception as e:
                logger.warning(f"等待搜索结果失败: {e}", exc_info=True)

            # 5. 切换标签
            if switch_tabs:
                logger.info(f"[5/6] 正在尝试切换到标签: {tab_type}")
                try:
                    tab_ele = tab.ele(f"text:{tab_type}", timeout=10)
                    if tab_ele:
                        tab_ele.click(by_js=True)
                        browser.wait(2)
                        logger.info(f"[OK] 切换到 {tab_type} 标签成功")
                    else:
                        logger.warning(f"未找到 {tab_type} 标签")
                except Exception as e:
                    logger.warning(f"切换标签失败: {e}", exc_info=True)

            # 6. 任务完成
            logger.info("[6/6] 测试任务执行完成")
            logger.info("=" * 50)
            logger.info("百度测试任务执行成功！")
            logger.info("=" * 50)

            return True

        except Exception as e:
            logger.error(f"百度测试业务执行失败: {str(e)}", exc_info=True)
            return False
