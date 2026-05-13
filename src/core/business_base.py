#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务基类 - 定义业务逻辑接口和自动注册机制
"""

import os
import importlib
from abc import ABC, abstractmethod
from typing import Dict, Any

# 业务注册表
_business_registry = {}

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
        print(f"警告: 业务 {name} 已存在，将被覆盖")
    
    _business_registry[name] = instance
    print(f"注册业务: {name} ({instance.get_display_name()})")

def get_business(name: str):
    """获取业务实例"""
    return _business_registry.get(name)

def get_all_businesses():
    """获取所有已注册的业务"""
    return list(_business_registry.values())

def discover_and_register_businesses(business_dir='src/business'):
    """自动发现并注册业务"""
    print("开始自动发现业务逻辑...")
    
    if not os.path.exists(business_dir):
        print(f"业务目录不存在: {business_dir}")
        return
    
    # 遍历业务目录
    for filename in os.listdir(business_dir):
        if filename.startswith('_') or not filename.endswith('.py'):
            continue
        
        module_name = filename[:-3]
        
        try:
            module = importlib.import_module(f'src.business.{module_name}')
            
            # 查找所有继承自 BaseBusiness 的类
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and issubclass(obj, BaseBusiness) and obj != BaseBusiness:
                    register_business(obj)
                    
        except Exception as e:
            print(f"加载业务模块失败 {module_name}: {e}")
    
    print(f"业务发现完成，共注册 {len(_business_registry)} 个业务")
