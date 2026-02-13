#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
足球数据分析预测主程序
整合所有模块，提供完整的预测功能
"""

import os
import sys
from typing import List, Optional
import argparse

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.data_processor import process_football_data
from src.trainers.baseline_trainer import BaselineTrainer, train_baselines_from_directories
from src.predictors.football_predictor import FootballPredictor
from src.models.data_models import MatchData, PredictionResult


class FootballAnalysisSystem:
    """足球数据分析系统主类"""
    
    def __init__(self, data_dirs: List[str] = None):
        """
        初始化系统
        
        Args:
            data_dirs: 数据目录列表
        """
        self.data_dirs = data_dirs or ['2021', '2023']
        self.matches = []
        self.trained_baselines = {}
        self.predictor = None
        
    def load_and_process_data(self, output_file: str = "processed_training_data.csv"):
        """
        加载并处理训练数据
        
        Args:
            output_file: 处理后数据的输出文件
        """
        print("=== 开始加载和处理数据 ===")
        self.matches = process_football_data(self.data_dirs, output_file)
        
        if not self.matches:
            raise ValueError("未能加载任何有效数据")
        
        print(f"成功加载 {len(self.matches)} 场比赛数据")
        return self.matches
    
    def train_baselines(self, output_file: str = "trained_baselines.json"):
        """
        训练联赛基线参数
        
        Args:
            output_file: 基线参数输出文件
        """
        print("\n=== 开始训练基线参数 ===")
        if not self.matches:
            self.load_and_process_data()
        
        trainer = BaselineTrainer()
        self.trained_baselines = trainer.train_from_matches(self.matches)
        trainer.save_baselines(self.trained_baselines, output_file)
        
        return self.trained_baselines
    
    def initialize_predictor(self, league: str = "中超"):
        """
        初始化预测器
        
        Args:
            league: 联赛名称
        """
        print(f"\n=== 初始化 {league} 联赛预测器 ===")
        self.predictor = FootballPredictor(league=league)
        return self.predictor
    
    def predict_single_match(self, home_team: str, away_team: str, 
                           league: str = "中超") -> PredictionResult:
        """
        预测单场比赛
        
        Args:
            home_team: 主队名称
            away_team: 客队名称
            league: 联赛名称
            
        Returns:
            PredictionResult: 预测结果
        """
        if not self.predictor:
            self.initialize_predictor(league)
        
        if not self.matches:
            self.load_and_process_data()
        
        # 创建虚拟比赛数据用于预测
        from src.models.data_models import MatchData
        mock_match = MatchData(
            match_id="PREDICTION",
            league=league,
            date="2024-01-01",
            home_team=home_team,
            away_team=away_team,
            home_goals=0,
            away_goals=0,
            home_shots=10,
            away_shots=10,
            home_shots_on_target=3,
            away_shots_on_target=3,
            home_possession=50.0,
            away_possession=50.0,
            home_pass_success=80.0,
            away_pass_success=80.0,
            home_fouls=12,
            away_fouls=12,
            home_yellow_cards=2,
            away_yellow_cards=2,
            home_corners=5,
            away_corners=5,
            home_red_cards=0,
            away_red_cards=0
        )
        
        result = self.predictor.predict_match(mock_match, self.matches)
        return result
    
    def batch_predict_matches(self, match_pairs: List[tuple], 
                            league: str = "中超") -> List[PredictionResult]:
        """
        批量预测多场比赛
        
        Args:
            match_pairs: 比赛对列表 [(主队, 客队), ...]
            league: 联赛名称
            
        Returns:
            List[PredictionResult]: 预测结果列表
        """
        if not self.predictor:
            self.initialize_predictor(league)
        
        results = []
        for home_team, away_team in match_pairs:
            result = self.predict_single_match(home_team, away_team, league)
            results.append(result)
        
        return results
    
    def cross_validation_evaluation(self, k_folds: int = 5):
        """
        进行交叉验证评估
        
        Args:
            k_folds: 折数
        """
        print("\n=== 开始交叉验证评估 ===")
        if not self.matches:
            self.load_and_process_data()
        
        trainer = BaselineTrainer()
        metrics = trainer.cross_validate(self.matches, k_folds)
        
        return metrics
    
    def interactive_prediction(self):
        """交互式预测模式"""
        print("\n=== 交互式预测模式 ===")
        print("请输入球队名称进行预测（输入 'quit' 退出）")
        
        while True:
            try:
                home_team = input("\n请输入主队名称: ").strip()
                if home_team.lower() == 'quit':
                    break
                    
                away_team = input("请输入客队名称: ").strip()
                if away_team.lower() == 'quit':
                    break
                
                league = input("请输入联赛名称（默认中超）: ").strip() or "中超"
                
                print(f"\n正在预测 {home_team} vs {away_team} ({league})...")
                result = self.predict_single_match(home_team, away_team, league)
                
                print("\n" + "="*50)
                print(f"比赛预测: {home_team} vs {away_team}")
                print("="*50)
                print(result)
                print("="*50)
                
            except KeyboardInterrupt:
                print("\n\n程序已退出")
                break
            except Exception as e:
                print(f"预测出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='足球数据分析预测系统')
    parser.add_argument('--mode', choices=['train', 'predict', 'evaluate', 'interactive'], 
                       default='interactive', help='运行模式')
    parser.add_argument('--data-dirs', nargs='+', default=['2021', '2023'], 
                       help='数据目录')
    parser.add_argument('--league', default='中超', help='联赛名称')
    parser.add_argument('--home-team', help='主队名称（预测模式）')
    parser.add_argument('--away-team', help='客队名称（预测模式）')
    parser.add_argument('--k-folds', type=int, default=5, help='交叉验证折数')
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = FootballAnalysisSystem(data_dirs=args.data_dirs)
    
    try:
        if args.mode == 'train':
            # 训练模式
            system.load_and_process_data()
            system.train_baselines()
            print("\n训练完成！")
            
        elif args.mode == 'predict':
            # 预测模式
            if args.home_team and args.away_team:
                result = system.predict_single_match(args.home_team, args.away_team, args.league)
                print(f"\n{args.home_team} vs {args.away_team} 预测结果:")
                print(result)
            else:
                print("预测模式需要指定 --home-team 和 --away-team 参数")
                
        elif args.mode == 'evaluate':
            # 评估模式
            metrics = system.cross_validation_evaluation(args.k_folds)
            print(f"\n评估完成，平均MAE: {metrics['avg_MAE_goals']:.3f}")
            
        elif args.mode == 'interactive':
            # 交互模式
            system.load_and_process_data()
            system.initialize_predictor(args.league)
            system.interactive_prediction()
            
    except Exception as e:
        print(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()