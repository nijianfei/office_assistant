#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 将应用打包为 EXE（集成 PyArmor 混淆）
"""

import os
import sys
import subprocess
import shutil
import time

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

def safe_remove_dir(path):
    """安全删除目录，处理文件被占用的情况"""
    if not os.path.exists(path):
        return True
    
    # 尝试终止可能占用该目录的进程
    for proc_name in ['办公助手.exe', 'OfficeAssistant.exe', 'python.exe']:
        try:
            subprocess.run(['taskkill', '/f', '/im', proc_name], 
                           capture_output=True, timeout=5)
        except:
            pass
    
    # 重试删除，最多重试3次
    for attempt in range(3):
        time.sleep(1)
        try:
            shutil.rmtree(path)
            print(f"清理目录: {path}")
            return True
        except PermissionError:
            if attempt < 2:
                print(f"重试删除目录 {path} ({attempt+1}/3)...")
                continue
            else:
                print(f"错误: 无法删除目录 {path}，文件可能被占用")
                print("请关闭所有正在运行的办公助手程序后重试")
                return False
        except Exception as e:
            print(f"删除目录失败 {path}: {e}")
            return False
    
    return False

def main():
    """主构建函数"""
    print("=" * 60)
    print("办公助手 - 构建脚本（集成 PyArmor 混淆）")
    print("=" * 60)

    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"项目目录: {project_dir}")

    # 1. 更新版本号
    print("\n[1/6] 更新版本号...")
    sys.path.insert(0, project_dir)
    from src.utils.version import increment_build_number, get_full_version
    increment_build_number()
    print(f"当前版本: {get_full_version()}")

    # 2. 检查并安装依赖
    print("\n[2/6] 检查依赖...")

    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("安装 PyInstaller...")
        if not run_command("pip install pyinstaller"):
            print("安装 PyInstaller 失败")
            return

    try:
        import pyarmor
        print("PyArmor 已安装")
    except ImportError:
        print("安装 PyArmor...")
        if not run_command("pip install pyarmor"):
            print("安装 PyArmor 失败")
            return

    print("安装项目依赖...")
    if not run_command("pip install -r requirements.txt", cwd=project_dir):
        print("安装依赖失败")
        return

    # 3. 创建打包目录
    print("\n[3/6] 创建打包目录...")

    obf_dir = os.path.join(project_dir, 'dist-obfuscated')
    if not safe_remove_dir(obf_dir):
        print("错误: 无法清理旧的打包目录，请关闭所有正在运行的办公助手程序后重试")
        return

    # 先复制非业务代码文件
    shutil.copytree(os.path.join(project_dir, 'src', 'core'), os.path.join(obf_dir, 'src', 'core'))
    shutil.copytree(os.path.join(project_dir, 'src', 'gui'), os.path.join(obf_dir, 'src', 'gui'))
    shutil.copytree(os.path.join(project_dir, 'src', 'models'), os.path.join(obf_dir, 'src', 'models'))
    shutil.copytree(os.path.join(project_dir, 'src', 'utils'), os.path.join(obf_dir, 'src', 'utils'))
    shutil.copy(os.path.join(project_dir, 'main.py'), obf_dir)
    shutil.copytree(os.path.join(project_dir, 'data'), os.path.join(obf_dir, 'data'))
    print("复制非业务代码文件完成")

    # 4. 使用 PyArmor 混淆业务代码
    print("\n[4/6] 使用 PyArmor 混淆业务代码...")

    business_src_dir = os.path.join(project_dir, 'src', 'business')
    business_dst_dir = os.path.join(obf_dir, 'src', 'business')

    pyarmor_cmd = f'pyarmor gen --output "{business_dst_dir}" --recursive "{business_src_dir}"'
    if not run_command(pyarmor_cmd, cwd=project_dir):
        print("PyArmor 混淆失败")
        return

    # 处理 PyArmor 生成的嵌套目录结构
    nested_business_dir = os.path.join(business_dst_dir, 'business')
    if os.path.exists(nested_business_dir):
        # 移动混淆后的文件到正确位置
        for item in os.listdir(nested_business_dir):
            src_item = os.path.join(nested_business_dir, item)
            dst_item = os.path.join(business_dst_dir, item)
            if os.path.isdir(src_item):
                shutil.move(src_item, dst_item)
            else:
                shutil.copy2(src_item, dst_item)
        # 删除空的嵌套目录
        shutil.rmtree(nested_business_dir)
        print("整理业务代码目录结构完成")

    # 5. 复制 PyArmor 运行时模块到 src 目录
    print("\n[4.5/6] 复制 PyArmor 运行时模块...")
    
    # PyArmor 会在混淆后的业务目录下生成运行时模块
    pyarmor_runtime_dir = os.path.join(business_dst_dir, 'pyarmor_runtime_000000')
    
    if os.path.exists(pyarmor_runtime_dir):
        # 将运行时模块复制到 src 目录下（这样才能被正确导入）
        target_runtime_dir = os.path.join(obf_dir, 'src', 'pyarmor_runtime_000000')
        safe_remove_dir(target_runtime_dir)
        shutil.copytree(pyarmor_runtime_dir, target_runtime_dir)
        print(f"复制 PyArmor 运行时模块到: {target_runtime_dir}")
        
        # 同时也要保留在 business 目录下的副本
        print("PyArmor 运行时模块已复制")
    else:
        print("警告: 未找到 PyArmor 运行时模块")

    # 6. 清理旧构建产物
    print("\n[5/6] 清理旧构建产物...")
    dist_dir = os.path.join(obf_dir, 'dist')
    build_dir = os.path.join(obf_dir, 'build')

    safe_remove_dir(dist_dir)
    safe_remove_dir(build_dir)

    # 7. 执行打包（添加 PyArmor 运行时支持）
    print("\n[6/6] 执行打包...")

    icon_path = os.path.join(project_dir, 'app.ico')
    icon_param = f'--icon="{icon_path}" ' if os.path.exists(icon_path) else ''

    obf_main = os.path.join(obf_dir, 'main.py')

    # 使用简化的打包命令，添加 PyArmor 运行时的隐藏导入
    cmd = (
        f'pyinstaller "{obf_main}" '
        f'--name "办公助手" '
        f'{icon_param}'
        f'--windowed '
        f'--onefile '
        f'--add-data "src;src" '
        f'--add-data "data;data" '
        f'--hidden-import="pyarmor_runtime_000000" '
    )

    if not run_command(cmd, cwd=obf_dir):
        print("打包失败")
        return

    print("\n" + "=" * 60)
    print("构建完成!")
    print(f"输出目录: {os.path.join(obf_dir, 'dist')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
