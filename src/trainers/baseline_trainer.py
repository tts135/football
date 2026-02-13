#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基线训练模块
基于历史数据训练联赛的基础统计参数
"""

import numpy as np
import pandas as pd
from collections import defaultdict
from typing import Dict, List, Tuple
import json

from ..models.data_models import MatchData
from ..config.league_coefficients import LEAGUE_COEFFICIENTS


class BaselineTrainer:
    """基线参数训练器"""
    
    def __init__(self):
        """初始化训练器"""
        self.league_stats = defaultdict(list)  # 存储各联赛的统计数据
    
    def collect_league_statistics(self, matches: List[MatchData]):
        """
        收集各联赛的统计数据
        
        Args:
            matches: 比赛数据列表
        """
        for match in matches:
            league = match.league
            
            # 收集各项统计数据
            self.league_stats[league].append({
                'total_goals': match.home_goals + match.away_goals,
                'total_corners': match.home_corners + match.away_corners,
                'total_yellow_cards': match.home_yellow_cards + match.away_yellow_cards,
                'home_goals': match.home_goals,
                'away_goals': match.away_goals,
                'home_possession': match.home_possession,
                'away_possession': match.away_possession,
                'home_fouls': match.home_fouls,
                'away_fouls': match.away_fouls
            })
    
    def calculate_league_baselines(self) -> Dict[str, Dict[str, float]]:
        """
        计算各联赛的基线参数
        
        Returns:
            Dict: 各联赛的基线系数
        """
        baselines = {}
        
        for league, stats_list in self.league_stats.items():
            if len(stats_list) < 10:  # 数据量太少的联赛跳过
                continue
                
            # 转换为numpy数组便于计算
            total_goals = np.array([s['total_goals'] for s in stats_list])
            total_corners = np.array([s['total_corners'] for s in stats_list])
            total_yellow = np.array([s['total_yellow_cards'] for s in stats_list])
            home_goals = np.array([s['home_goals'] for s in stats_list])
            away_goals = np.array([s['away_goals'] for s in stats_list])
            home_fouls = np.array([s['home_fouls'] for s in stats_list])
            away_fouls = np.array([s['away_fouls'] for s in stats_list])
            
            # 计算基本统计量
            avg_total_goals = np.mean(total_goals)
            avg_total_corners = np.mean(total_corners)
            avg_total_yellow = np.mean(total_yellow)
            
            # 计算主场优势（主场进球/客场进球）
            home_advantage = np.mean(home_goals) / (np.mean(away_goals) + 1e-8)
            
            # 计算犯规到黄牌的转换率
            total_fouls = np.mean(home_fouls + away_fouls)
            foul_to_yellow_ratio = avg_total_yellow / (total_fouls + 1e-8)
            
            # 构造基线系数
            baselines[league] = {
                'goal_baseline': float(avg_total_goals),
                'corner_baseline': float(avg_total_corners),
                'yellow_card_baseline': float(avg_total_yellow),
                'home_advantage': float(home_advantage),
                'foul_to_yellow': float(foul_to_yellow_ratio),
                'red_card_penalty': 2.0,  # 红牌折算保持默认值
                'sample_size': len(stats_list)
            }
        
        return baselines
    
    def train_from_matches(self, matches: List[MatchData]) -> Dict[str, Dict[str, float]]:
        """
        从比赛数据训练基线参数
        
        Args:
            matches: 比赛数据列表
            
        Returns:
            Dict: 训练得到的基线系数
        """
        print(f"开始训练基线参数，共 {len(matches)} 场比赛...")
        
        # 收集统计数据
        self.collect_league_statistics(matches)
        
        # 计算基线参数
        baselines = self.calculate_league_baselines()
        
        # 显示训练结果
        print("\n训练完成！各联赛基线参数:")
        print("-" * 50)
        for league, params in baselines.items():
            print(f"\n{league} (样本数: {params['sample_size']}):")
            print(f"  场均总进球: {params['goal_baseline']:.2f}")
            print(f"  场均总角球: {params['corner_baseline']:.2f}")
            print(f"  场均总黄牌: {params['yellow_card_baseline']:.2f}")
            print(f"  主场优势系数: {params['home_advantage']:.3f}")
            print(f"  犯规转黄牌系数: {params['foul_to_yellow']:.3f}")
        
        return baselines
    
    def save_baselines(self, baselines: Dict[str, Dict[str, float]], file_path: str):
        """
        保存训练得到的基线参数
        
        Args:
            baselines: 基线参数字典
            file_path: 保存文件路径
        """
        # 转换为可序列化的格式
        serializable_baselines = {}
        for league, params in baselines.items():
            serializable_baselines[league] = {
                'goal_baseline': float(params['goal_baseline']),
                'corner_baseline': float(params['corner_baseline']),
                'yellow_card_baseline': float(params['yellow_card_baseline']),
                'home_advantage': float(params['home_advantage']),
                'foul_to_yellow': float(params['foul_to_yellow']),
                'red_card_penalty': float(params['red_card_penalty']),
                'sample_size': int(params['sample_size'])
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_baselines, f, indent=2, ensure_ascii=False)
        
        print(f"\n基线参数已保存到: {file_path}")
    
    def evaluate_predictions(self, predictions: List[Tuple[float, float]], 
                           actual_results: List[Tuple[int, int]]) -> Dict[str, float]:
        """
        评估预测效果
        
        Args:
            predictions: 预测结果 [(主队进球, 客队进球), ...]
            actual_results: 实际结果 [(主队进球, 客队进球), ...]
            
        Returns:
            Dict: 评估指标
        """
        if len(predictions) != len(actual_results):
            raise ValueError("预测数量与实际结果数量不匹配")
        
        # 计算各种误差指标
        mae_goals = []  # 平均绝对误差
        rmse_goals = []  # 均方根误差
        correct_direction = 0  # 胜平负方向正确的次数
        
        total_predictions = len(predictions)
        
        for pred, actual in zip(predictions, actual_results):
            pred_home, pred_away = pred
            actual_home, actual_away = actual
            
            # 进球数误差
            home_error = abs(pred_home - actual_home)
            away_error = abs(pred_away - actual_away)
            mae_goals.extend([home_error, away_error])
            rmse_goals.extend([(pred_home - actual_home)**2, (pred_away - actual_away)**2])
            
            # 胜平负方向判断
            pred_result = "win" if pred_home > pred_away else "draw" if pred_home == pred_away else "lose"
            actual_result = "win" if actual_home > actual_away else "draw" if actual_home == actual_away else "lose"
            
            if pred_result == actual_result:
                correct_direction += 1
        
        # 计算最终指标
        metrics = {
            'MAE_goals': np.mean(mae_goals),
            'RMSE_goals': np.sqrt(np.mean(rmse_goals)),
            'accuracy_direction': correct_direction / total_predictions,
            'total_samples': total_predictions
        }
        
        return metrics
    
    def cross_validate(self, matches: List[MatchData], k_folds: int = 5) -> Dict[str, float]:
        """
        K折交叉验证评估模型性能
        
        Args:
            matches: 比赛数据
            k_folds: 折数
            
        Returns:
            Dict: 平均评估指标
        """
        from ..predictors.football_predictor import FootballPredictor
        
        # 随机打乱数据
        np.random.shuffle(matches)
        
        fold_size = len(matches) // k_folds
        all_metrics = []
        
        print(f"\n开始 {k_folds} 折交叉验证...")
        
        for fold in range(k_folds):
            # 分割训练集和测试集
            test_start = fold * fold_size
            test_end = test_start + fold_size if fold < k_folds - 1 else len(matches)
            
            test_matches = matches[test_start:test_end]
            train_matches = matches[:test_start] + matches[test_end:]
            
            # 训练基线参数
            temp_trainer = BaselineTrainer()
            baselines = temp_trainer.train_from_matches(train_matches)
            
            # 进行预测
            predictor = FootballPredictor()
            predictions = []
            actual_results = []
            
            for match in test_matches:
                pred_result = predictor.predict_match(match, train_matches)
                predictions.append((pred_result.home_team_goals, pred_result.away_team_goals))
                actual_results.append((match.home_goals, match.away_goals))
            
            # 评估
            metrics = self.evaluate_predictions(predictions, actual_results)
            all_metrics.append(metrics)
            
            print(f"第 {fold + 1} 折 - MAE: {metrics['MAE_goals']:.3f}, "
                  f"准确率: {metrics['accuracy_direction']:.3f}")
        
        # 计算平均指标
        avg_metrics = {
            'avg_MAE_goals': np.mean([m['MAE_goals'] for m in all_metrics]),
            'avg_RMSE_goals': np.mean([m['RMSE_goals'] for m in all_metrics]),
            'avg_accuracy_direction': np.mean([m['accuracy_direction'] for m in all_metrics]),
            'std_MAE_goals': np.std([m['MAE_goals'] for m in all_metrics])
        }
        
        print(f"\n交叉验证结果:")
        print(f"平均MAE: {avg_metrics['avg_MAE_goals']:.3f} ± {avg_metrics['std_MAE_goals']:.3f}")
        print(f"平均准确率: {avg_metrics['avg_accuracy_direction']:.3f}")
        
        return avg_metrics


# 便捷训练函数
def train_baselines_from_directories(directories: List[str], 
                                   output_file: str = "trained_baselines.json") -> Dict[str, Dict[str, float]]:
    """
    从目录训练基线参数的便捷函数
    
    Args:
        directories: 数据目录列表
        output_file: 输出文件名
        
    Returns:
        Dict: 训练得到的基线参数
    """
    from ..data.data_processor import process_football_data
    
    # 处理数据
    print("正在处理训练数据...")
    matches = process_football_data(directories)
    
    if not matches:
        raise ValueError("没有找到有效的训练数据")
    
    # 训练基线参数
    trainer = BaselineTrainer()
    baselines = trainer.train_from_matches(matches)
    
    # 保存结果
    trainer.save_baselines(baselines, output_file)
    
    return baselines