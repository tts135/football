#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行预测统一入口脚本
"""

import os
import sys
import argparse

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.main import FootballAnalysisSystem

def main():
    parser = argparse.ArgumentParser(description='足球比赛预测系统')
    parser.add_argument('--home-team', required=True, help='主队名称')
    parser.add_argument('--away-team', required=True, help='客队名称')
    parser.add_argument('--league', default='中超', help='联赛名称')
    parser.add_argument('--data-dir', default=os.path.join(project_root, 'data', 'processed'),
                       help='处理后的数据目录')
    
    args = parser.parse_args()
    
    # 初始化系统
    system = FootballAnalysisSystem(data_dirs=[args.data-dir])
    
    try:
        print(f"=== 预测 {args.home_team} vs {args.away_team} ({args.league}) ===")
        
        # 加载数据和初始化预测器
        system.load_and_process_data(output_file=os.path.join(args.data-dir, 'processed_training_data.csv'))
        system.initialize_predictor(args.league)
        
        # 进行预测
        result = system.predict_single_match(args.home_team, args.away_team, args.league)
        
        print("\n" + "="*60)
        print(f"比赛预测结果: {args.home_team} vs {args.away_team}")
        print("="*60)
        print(f"预测比分: {result.prediction.home_team_goals:.1f} - {result.prediction.away_team_goals:.1f}")
        print(f"总进球数: {result.prediction.total_goals:.1f}")
        print(f"角球预测: {result.prediction.home_corners:.1f} - {result.prediction.away_corners:.1f}")
        print(f"黄牌预测: {result.prediction.home_yellow_cards:.1f} - {result.prediction.away_yellow_cards:.1f}")
        print(f"胜率: 主队 {result.prediction.home_win_probability:.1%}, 客队 {result.prediction.away_win_probability:.1%}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 预测出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()