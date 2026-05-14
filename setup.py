#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cython 编译配置文件
编译核心安全模块为 C 扩展
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# 需要编译的核心模块
core_modules = [
    'src/utils/license_manager.py',
    'src/utils/trial_manager.py'
]

def get_extension(module_path):
    """创建 Cython 扩展"""
    # 移除 .py 后缀，转换为模块路径
    module_name = module_path.replace('/', '.').replace('.py', '')
    return Extension(
        module_name,
        [module_path],
        extra_compile_args=['-O2'],  # 优化级别
        language='c'
    )

def main():
    """主编译函数"""
    print("=" * 60)
    print("Cython 编译核心模块")
    print("=" * 60)
    
    # 创建扩展列表
    extensions = [get_extension(module) for module in core_modules]
    
    # 编译
    setup(
        name='office_assistant_core',
        ext_modules=cythonize(extensions, 
                              language_level="3",
                              build_dir="build/cython"),
        zip_safe=False
    )
    
    print("\n编译完成！")

if __name__ == "__main__":
    main()
