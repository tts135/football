#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目清理脚本
删除多余的文件和旧的脚本
"""

import os
import sys
import shutil

def cleanup_files():
    """清理多余文件"""
    print("=== 开始清理多余文件 ===")
    
    # 要删除的文件列表
    files_to_remove = [
        'BothTeamDataProcess.py',
        'CornerBallStatistics.py',
        'features.py',
        'new.py',
        'simple_test.py',
        'football.csv',
        'bothTeamData.csv',
        'processed_data.csv',
        'CornerBallStatistics_output.csv',
        '~$football.csv',
        '2021.rar'
    ]
    
    # 要删除的目录（空目录）
    dirs_to_remove = [
        'notebooks',
        'docs',
        'tests'
    ]
    
    removed_count = 0
    
    # 删除文件
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ 删除: {file}")
                removed_count += 1
            except Exception as e:
                print(f"❌ 无法删除 {file}: {e}")
    
    # 删除空目录
    for directory in dirs_to_remove:
        if os.path.exists(directory) and not os.listdir(directory):
            try:
                os.rmdir(directory)
                print(f"✅ 删除空目录: {directory}")
                removed_count += 1
            except Exception as e:
                print(f"❌ 无法删除目录 {directory}: {e}")
    
    print(f"\n清理完成！共删除 {removed_count} 个文件/目录")
    return removed_count

def organize_data():
    """整理数据文件到新目录"""
    print("\n=== 整理数据文件 ===")
    
    # 将2021和2023目录移动到data/raw/
    data_dirs = ['2021', '2023']
    target_base = os.path.join('data', 'raw')
    
    for dir_name in data_dirs:
        if os.path.exists(dir_name):
            target_path = os.path.join(target_base, dir_name)
            try:
                shutil.move(dir_name, target_path)
                print(f"✅ 移动: {dir_name} -> {target_path}")
            except Exception as e:
                print(f"❌ 无法移动 {dir_name}: {e}")
    
    # 复制必要的配置文件
    config_files = ['requirements.txt', 'README.md', '设计文档.md']
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                shutil.copy(config_file, '.')
                print(f"✅ 复制配置文件: {config_file}")
            except Exception as e:
                print(f"❌ 无法复制 {config_file}: {e}")

def main():
    print("🧹 足球数据分析项目清理工具")
    print("=" * 50)
    
    # 执行清理
    cleanup_files()
    
    # 整理数据
    organize_data()
    
    print("\n✅ 清理完成！")
    print("\n新的项目结构:")
    print("├── data/")
    print("│   ├── raw/")
    print("│   │   ├── 2021/")
    print("│   │   └── 2023/")
    print("│   └── processed/")
    print("├── src/")
    print("├── webapp/")
    print("├── scripts/")
    print("├── models/")
    print("└── run.bat (统一启动脚本)")

if __name__ == "__main__":
    main()
