#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务基类 - 定义业务逻辑接口和自动注册机制
"""

import os
import sys
import importlib
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.utils.logger import logger

# 业务注册表
_business_registry = {}

# 已知的业务模块列表（打包时需要预先定义）
_KNOWN_BUSINESS_MODULES = [
    'baidu_test',
    # 添加其他业务模块...
]

class BaseBusiness(ABC):
    """业务基类 - 所有业务逻辑必须继承此类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """获取业务唯一标识"""
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """获取业务显示名称"""
        pass
    
    def get_description(self) -> str:
        """获取业务描述"""
        return ""
    
    def get_param_schema(self) -> Dict[str, Any]:
        """获取参数Schema"""
        return {}
    
    @abstractmethod
    def execute(self, browser, **kwargs) -> bool:
        """执行业务逻辑"""
        pass

def register_business(business_class):
    """注册业务类"""
    if not issubclass(business_class, BaseBusiness):
        raise ValueError("业务类必须继承 BaseBusiness")
    
    instance = business_class()
    name = instance.get_name()
    
    if name in _business_registry:
        logger.debug(f"业务 {name} 已存在，跳过注册")
        return
    
    _business_registry[name] = instance
    logger.info(f"注册业务: {name} ({instance.get_display_name()})")
    return business_class

def business(cls):
    """业务类装饰器 - 简化业务注册"""
    return register_business(cls)

def get_business(name: str):
    """获取业务实例"""
    return _business_registry.get(name)

def get_all_businesses():
    """获取所有已注册的业务"""
    return list(_business_registry.values())

def is_frozen():
    """检查是否是打包后的环境"""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def discover_and_register_businesses():
    """自动发现并注册业务
    
    开发阶段：扫描 src/business 目录
    打包后：直接导入已知的业务模块
    
    注意：业务模块需要在模块级别使用 @business 装饰器自动注册
    """
    logger.info("开始自动发现业务逻辑...")
    
    if is_frozen():
        # 打包后：直接导入已知的业务模块（依赖模块内部自动注册）
        logger.info("检测到打包环境，使用预设业务列表")
        for module_name in _KNOWN_BUSINESS_MODULES:
            try:
                # 直接导入模块，业务类会通过装饰器自动注册
                importlib.import_module(f'src.business.{module_name}')
                logger.debug(f"导入业务模块: {module_name}")
            except Exception as e:
                logger.error(f"加载业务模块失败 {module_name}: {e}")
    else:
        # 开发阶段：扫描业务目录
        business_dir = 'src/business'
        logger.debug(f"业务目录: {business_dir}")
        
        if not os.path.exists(business_dir):
            logger.warning(f"业务目录不存在: {business_dir}")
            return
        
        # 遍历业务目录
        for filename in os.listdir(business_dir):
            if filename.startswith('_') or not filename.endswith('.py'):
                continue
            
            module_name = filename[:-3]
            
            try:
                # 直接导入模块，业务类会通过装饰器自动注册
                importlib.import_module(f'src.business.{module_name}')
                logger.debug(f"导入业务模块: {module_name}")
            except Exception as e:
                logger.error(f"加载业务模块失败 {module_name}: {e}")
    
    logger.info(f"业务发现完成，共注册 {len(_business_registry)} 个业务")
