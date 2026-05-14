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

def run_command(cmd, cwd=None, shell=True):
    """运行命令并返回结果
    
    Args:
        cmd: 命令字符串或参数列表
        cwd: 工作目录
        shell: 是否使用 shell 执行（默认 True 保持向后兼容）
    """
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

def safe_remove_dir(path):
    """安全删除目录，处理文件被占用的情况"""
    print(f"safe_remove_dir: 尝试删除目录: {path}")
    if not os.path.exists(path):
        print("safe_remove_dir: 目录不存在，直接返回")
        return True
    
    # 尝试终止可能占用该目录的进程（不终止当前脚本的python进程）
    print("safe_remove_dir: 尝试终止可能占用该目录的进程...")
    for proc_name in ['办公助手.exe', 'OfficeAssistant.exe']:
        try:
            print(f"safe_remove_dir: 尝试终止进程: {proc_name}")
            result = subprocess.run(['taskkill', '/f', '/im', proc_name], 
                                   capture_output=True, timeout=5)
            print(f"safe_remove_dir: taskkill 返回码: {result.returncode}")
        except Exception as e:
            print(f"safe_remove_dir: 终止进程失败 {proc_name}: {e}")
    
    # 重试删除，最多重试3次
    print("safe_remove_dir: 开始尝试删除目录...")
    for attempt in range(3):
        print(f"safe_remove_dir: 尝试 {attempt+1}/3...")
        time.sleep(1)
        try:
            shutil.rmtree(path)
            print(f"safe_remove_dir: 成功清理目录: {path}")
            return True
        except PermissionError:
            print(f"safe_remove_dir: PermissionError - 文件被占用")
            if attempt < 2:
                print(f"safe_remove_dir: 重试删除目录 {path} ({attempt+1}/3)...")
                continue
            else:
                print(f"safe_remove_dir: 错误: 无法删除目录 {path}，文件可能被占用")
                print("safe_remove_dir: 请关闭所有正在运行的办公助手程序后重试")
                return False
        except Exception as e:
            print(f"safe_remove_dir: 删除目录失败 {path}: {type(e).__name__}: {e}")
            return False
    
    print("safe_remove_dir: 循环结束，返回 False")
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
    print(f"目标目录: {obf_dir}")
    
    # 尝试删除旧目录，如果失败则尝试强制删除
    if os.path.exists(obf_dir):
        print("旧目录存在，尝试删除...")
        if not safe_remove_dir(obf_dir):
            # 如果安全删除失败，尝试强制删除
            print("尝试强制删除旧目录...")
            try:
                # 先删除所有文件
                for root, dirs, files in os.walk(obf_dir, topdown=False):
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                        except:
                            pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except:
                            pass
                # 最后删除根目录
                if os.path.exists(obf_dir):
                    os.rmdir(obf_dir)
                print(f"强制清理目录：{obf_dir}")
            except Exception as e:
                print(f"错误：无法清理目录 {obf_dir}: {e}")
                print("请手动删除该目录后重试")
                return
    else:
        print("旧目录不存在，跳过删除")
    
    # 创建新目录
    print("创建新目录...")
    os.makedirs(obf_dir, exist_ok=True)
    print(f"创建目录: {obf_dir}")
    os.makedirs(os.path.join(obf_dir, 'src'), exist_ok=True)
    print(f"创建目录: {os.path.join(obf_dir, 'src')}")
    print("目录创建完成")

    # 先复制非业务代码文件
    try:
        print("复制 core 目录...")
        shutil.copytree(os.path.join(project_dir, 'src', 'core'), os.path.join(obf_dir, 'src', 'core'), dirs_exist_ok=True)
        print("复制 gui 目录...")
        shutil.copytree(os.path.join(project_dir, 'src', 'gui'), os.path.join(obf_dir, 'src', 'gui'), dirs_exist_ok=True)
        print("复制 models 目录...")
        shutil.copytree(os.path.join(project_dir, 'src', 'models'), os.path.join(obf_dir, 'src', 'models'), dirs_exist_ok=True)
        print("复制 utils 目录...")
        shutil.copytree(os.path.join(project_dir, 'src', 'utils'), os.path.join(obf_dir, 'src', 'utils'), dirs_exist_ok=True)
        print("复制 main.py...")
        shutil.copy(os.path.join(project_dir, 'main.py'), obf_dir)
        print("复制 data 目录...")
        shutil.copytree(os.path.join(project_dir, 'data'), os.path.join(obf_dir, 'data'), dirs_exist_ok=True)
        print("复制非业务代码文件完成")
    except Exception as e:
        print(f"错误：复制文件失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 使用 PyArmor 混淆业务代码
    print("\n[4/6] 使用 PyArmor 混淆业务代码...")

    business_src_dir = os.path.join(project_dir, 'src', 'business')
    business_dst_dir = os.path.join(obf_dir, 'src', 'business')

    # 使用列表形式传递参数，避免路径空格问题
    pyarmor_cmd = ['pyarmor', 'gen', '--output', business_dst_dir, '--recursive', business_src_dir]
    if not run_command(pyarmor_cmd, cwd=project_dir, shell=False):
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
    
    dist_path = os.path.join(obf_dir, 'dist')
    build_path = os.path.join(obf_dir, 'build')

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
        f'--distpath "{dist_path}" '
        f'--workpath "{build_path}" '
        f'--specpath "{obf_dir}" '
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
