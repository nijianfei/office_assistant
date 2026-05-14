#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本 - 清理缓存文件、构建产物和日志
"""

import os
import shutil
import subprocess

def remove_dir(path):
    """删除目录"""
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"删除目录: {path}")

def remove_file(path):
    """删除文件"""
    if os.path.exists(path):
        os.remove(path)
        print(f"删除文件: {path}")

def find_and_remove_pycache(root_dir):
    """查找并删除所有 __pycache__ 目录"""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            shutil.rmtree(pycache_path)
            print(f"删除缓存目录: {pycache_path}")

def find_and_remove_pyc_files(root_dir):
    """查找并删除所有 .pyc 文件"""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_path = os.path.join(dirpath, filename)
                os.remove(pyc_path)
                print(f"删除字节码文件: {pyc_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("办公助手 - 项目清理脚本")
    print("=" * 60)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"项目目录: {project_dir}\n")
    
    # 1. 终止可能运行的进程
    print("[1/5] 终止可能运行的进程...")
    for proc_name in ['办公助手.exe', 'OfficeAssistant.exe']:
        try:
            subprocess.run(['taskkill', '/f', '/im', proc_name], 
                           capture_output=True, timeout=5)
        except:
            pass
    
    # 2. 删除 PyInstaller 构建产物
    print("\n[2/5] 删除构建产物...")
    remove_dir(os.path.join(project_dir, 'build'))
    remove_dir(os.path.join(project_dir, 'dist'))
    remove_dir(os.path.join(project_dir, 'dist-obfuscated'))
    
    # 3. 删除缓存目录和文件
    print("\n[3/5] 删除 Python 缓存...")
    find_and_remove_pycache(project_dir)
    find_and_remove_pyc_files(project_dir)
    
    # 4. 删除日志文件（保留最近7天的）
    print("\n[4/5] 删除日志文件...")
    logs_dir = os.path.join(project_dir, 'logs')
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith('.log'):
                log_path = os.path.join(logs_dir, filename)
                os.remove(log_path)
                print(f"删除日志文件: {log_path}")
    
    # 5. 删除其他临时文件
    print("\n[5/5] 删除其他临时文件...")
    remove_file(os.path.join(project_dir, 'build_output.log'))
    remove_file(os.path.join(project_dir, 'pyarmor.bug.log'))
    remove_file(os.path.join(project_dir, 'debug.log'))
    remove_file(os.path.join(project_dir, 'trial.dat'))
    
    print("\n" + "=" * 60)
    print("清理完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
