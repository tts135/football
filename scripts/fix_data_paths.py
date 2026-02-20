#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据路径问题的脚本
将 data/raw/2021/2021/* 移动到 data/raw/2021/
将 data/raw/2023/2023/* 移动到 data/raw/2023/
"""

import os
import shutil
import sys

def fix_data_paths():
    """修复数据路径"""
    print("=== 修复数据路径 ===")
    
    # 定义源路径和目标路径
    paths_to_fix = [
        ('data/raw/2021', '2021'),
        ('data/raw/2023', '2023')
    ]
    
    for base_dir, sub_dir in paths_to_fix:
        source_path = os.path.join(base_dir, sub_dir)
        target_path = base_dir
        
        if os.path.exists(source_path):
            print(f"发现嵌套目录: {source_path}")
            
            # 获取源目录中的所有文件
            files = [f for f in os.listdir(source_path) if os.path.isfile(os.path.join(source_path, f))]
            
            if files:
                print(f"找到 {len(files)} 个文件在 {source_path}")
                
                # 创建目标目录（如果不存在）
                os.makedirs(target_path, exist_ok=True)
                
                # 移动文件
                for file in files:
                    src_file = os.path.join(source_path, file)
                    dst_file = os.path.join(target_path, file)
                    
                    try:
                        shutil.move(src_file, dst_file)
                        print(f"✅ 移动: {file} -> {target_path}")
                    except Exception as e:
                        print(f"❌ 无法移动 {file}: {e}")
                
                # 如果源目录为空，删除它
                if not os.listdir(source_path):
                    try:
                        os.rmdir(source_path)
                        print(f"✅ 删除空目录: {source_path}")
                    except Exception as e:
                        print(f"❌ 无法删除目录 {source_path}: {e}")
            else:
                print(f"源目录 {source_path} 中没有文件")
        else:
            print(f"路径 {source_path} 不存在，跳过")
    
    print("=== 路径修复完成 ===")

if __name__ == "__main__":
    fix_data_paths()