#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单构建脚本 - 非混淆版本
输出路径: dist/
"""
import subprocess
import sys
import os
import shutil

def run_command(cmd, cwd=None, shell=True):
    """运行命令并返回结果"""
    if isinstance(cmd, list):
        cmd_str = ' '.join(cmd)
    else:
        cmd_str = cmd
    
    print(f"执行命令：{cmd_str}")
    try:
        result = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"错误：{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令失败：{e}")
        return False

def main():
    # 动态获取项目目录（避免硬编码）
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, 'dist')
    build_dir = os.path.join(project_dir, 'build')

    print("=" * 60)
    print("办公助手 - 简单构建脚本（非混淆版本）")
    print("=" * 60)
    print(f"项目目录: {project_dir}")
    print(f"输出目录: {dist_dir}")
    print(f"Python 版本: {sys.version}")

    # 检查并安装依赖
    print("\n检查依赖...")

    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("安装 PyInstaller...")
        if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller']):
            print("安装 PyInstaller 失败")
            sys.exit(1)

    print("安装项目依赖...")
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=project_dir):
        print("安装依赖失败")
        sys.exit(1)

    # 清理旧构建产物
    if os.path.exists(dist_dir):
        print("清理旧的 dist 目录...")
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        print("清理旧的 build 目录...")
        shutil.rmtree(build_dir)

    os.chdir(project_dir)

    cmd = [
        sys.executable,
        '-m', 'PyInstaller',
        'main.py',
        '--name', '办公助手',
        '--windowed',
        '--onefile',
        '--add-data', 'src;src',
        '--add-data', 'data;data',
        '--distpath', dist_dir,
        '--workpath', build_dir,
        '--hidden-import', 'src.utils.license_manager',
        '--hidden-import', 'src.utils.trial_manager',
        '--hidden-import', 'src.utils.version',
        '--hidden-import', 'src.gui.main_window',
        '--hidden-import', 'src.gui.license_dialog',
        '--hidden-import', 'DrissionPage',
        '--hidden-import', 'psutil',
        '--hidden-import', 'cryptography',
        '--hidden-import', 'sqlalchemy',
        '--hidden-import', 'PyQt6',
        '--hidden-import', 'PyQt6.QtWidgets',
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtGui',
    ]

    print("\n开始打包（不混淆）...")
    # 使用直接输出模式
    result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("构建完成!")
        print(f"输出目录: {dist_dir}")
        print("=" * 60)
    else:
        print(f"\n打包失败，返回码: {result.returncode}")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
