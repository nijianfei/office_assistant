#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import shutil

project_dir = r'c:\Users\njf\Documents\trae_projects\TEST_PROJECT\office_assistant_new'
dist_dir = os.path.join(project_dir, 'dist')
build_dir = os.path.join(project_dir, 'build')

if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
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

print("开始打包（不混淆）...")
result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)
print(f"打包完成，返回码: {result.returncode}")
sys.exit(result.returncode)
