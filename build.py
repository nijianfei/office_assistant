#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 将应用打包为 EXE
"""

import os
import sys
import subprocess
import shutil

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"错误: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令失败: {e}")
        return False

def main():
    """主构建函数"""
    print("=" * 60)
    print("办公助手 - 构建脚本")
    print("=" * 60)
    
    # 当前目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"项目目录: {project_dir}")
    
    # 1. 更新版本号
    print("\n[1/4] 更新版本号...")
    sys.path.insert(0, project_dir)
    from src.utils.version import increment_build_number, get_full_version
    increment_build_number()
    print(f"当前版本: {get_full_version()}")
    
    # 2. 检查并安装依赖
    print("\n[2/4] 检查依赖...")
    
    # 检查 pyinstaller
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("安装 PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("安装 PyInstaller 失败")
            return
    
    # 安装项目依赖
    print("安装项目依赖...")
    if not run_command("pip install -r requirements.txt", cwd=project_dir):
        print("安装依赖失败")
        return
    
    # 3. 清理旧构建产物
    print("\n[3/4] 清理旧构建产物...")
    dist_dir = os.path.join(project_dir, 'dist')
    build_dir = os.path.join(project_dir, 'build')
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
        print(f"删除目录: {dist_dir}")
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"删除目录: {build_dir}")
    
    # 4. 执行打包
    print("\n[4/4] 执行打包...")
    
    # 检查图标文件是否存在
    icon_param = '--icon=app.ico ' if os.path.exists('app.ico') else ''
    
    # PyInstaller 命令
    cmd = (
        f'pyinstaller main.py '
        f'--name "办公助手" '
        f'{icon_param}'
        f'--windowed '
        f'--onefile '
        f'--add-data "src;src" '
        f'--add-data "data;data" '
        f'--hidden-import="src.utils.license_manager" '
        f'--hidden-import="src.utils.trial_manager" '
        f'--hidden-import="src.utils.version" '
        f'--hidden-import="src.gui.main_window" '
        f'--hidden-import="src.gui.license_dialog" '
        f'--hidden-import="DrissionPage" '
        f'--hidden-import="psutil" '
        f'--hidden-import="cryptography" '
        f'--hidden-import="schedule" '
        f'--hidden-import="sqlalchemy" '
        f'--hidden-import="PyQt6" '
    )
    
    if not run_command(cmd, cwd=project_dir):
        print("打包失败")
        return
    
    # 复制数据目录到 dist
    src_data = os.path.join(project_dir, 'data')
    dist_data = os.path.join(dist_dir, 'data')
    if os.path.exists(src_data) and not os.path.exists(dist_data):
        shutil.copytree(src_data, dist_data)
        print(f"复制数据目录: {src_data} -> {dist_data}")
    
    print("\n" + "=" * 60)
    print("构建完成!")
    print(f"输出目录: {dist_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()
