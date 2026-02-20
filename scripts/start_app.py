#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用统一启动脚本
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 启动足球数据分析Web应用...")
    
    # 设置路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    webapp_dir = os.path.join(project_root, 'webapp')
    
    # 检查依赖
    try:
        import flask
        import pandas
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 检查数据目录
    data_dirs = [
        os.path.join(project_root, 'data', 'raw', '2021'),
        os.path.join(project_root, 'data', 'raw', '2023')
    ]
    
    data_exists = all(os.path.exists(d) for d in data_dirs)
    if not data_exists:
        print("⚠️  数据目录不存在，建议先运行 setup_data.py 处理数据")
    
    # 启动Web应用
    print(f"🔧 启动Web应用，工作目录: {webapp_dir}")
    
    try:
        # 使用子进程启动
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=webapp_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待应用启动
        time.sleep(2)
        
        print("✅ Web应用启动成功！")
        print("🌐 访问地址: http://localhost:5000")
        print("📊 大屏界面: http://localhost:5000")
        print("🎯 预测界面: http://localhost:5000/predict")
        
        # 显示进程信息
        print(f"\nPID: {process.pid}")
        print("按 Ctrl+C 停止应用")
        
        # 等待进程结束
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止应用...")
            process.terminate()
            
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()