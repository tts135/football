#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型训练统一入口脚本
"""

import os
import sys
import argparse

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.main import FootballAnalysisSystem

def main():
    parser = argparse.ArgumentParser(description='足球数据分析模型训练')
    parser.add_argument('--data-dir', default=os.path.join(project_root, 'data', 'processed'),
                       help='处理后的数据目录')
    parser.add_argument('--output-dir', default=os.path.join(project_root, 'models'),
                       help='模型输出目录')
    parser.add_argument('--mode', choices=['train', 'evaluate'], default='train',
                       help='运行模式')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 初始化系统
    system = FootballAnalysisSystem(data_dirs=[args.data-dir])
    
    if args.mode == 'train':
        print("=== 开始训练模型 ===")
        system.load_and_process_data(output_file=os.path.join(args.output_dir, 'processed_training_data.csv'))
        system.train_baselines(output_file=os.path.join(args.output_dir, 'trained_baselines.json'))
        print("✅ 训练完成！")
        
    elif args.mode == 'evaluate':
        print("=== 开始评估模型 ===")
        system.load_and_process_data(output_file=os.path.join(args.output_dir, 'processed_training_data.csv'))
        metrics = system.cross_validation_evaluation(k_folds=5)
        print(f"✅ 评估完成，平均MAE: {metrics['avg_MAE_goals']:.3f}")
    
    print(f"模型文件已保存到: {args.output_dir}")

if __name__ == "__main__":
    main()