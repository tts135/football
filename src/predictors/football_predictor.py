#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
足球预测核心模块
基于统计基线法 + 联赛特征修正进行预测
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict

from ..models.data_models import MatchData, TeamStats, PredictionResult
from ..config.league_coefficients import LEAGUE_COEFFICIENTS, DEFAULT_LEAGUE, DATA_CONFIG


class FootballPredictor:
    """足球数据预测器"""
    
    def __init__(self, league: str = DEFAULT_LEAGUE):
        """
        初始化预测器
        
        Args:
            league: 联赛名称
        """
        self.league = league
        self.coefficients = LEAGUE_COEFFICIENTS.get(league, LEAGUE_COEFFICIENTS[DEFAULT_LEAGUE])
        self.team_stats_cache = {}  # 缓存球队统计数据
        
    def calculate_team_stats(self, matches: List[MatchData], team_name: str, 
                           recent_n: int = DATA_CONFIG["recent_matches_window"]) -> TeamStats:
        """
        计算球队的历史统计数据
        
        Args:
            matches: 比赛数据列表
            team_name: 球队名称
            recent_n: 使用最近N场比赛
            
        Returns:
            TeamStats: 球队统计数据
        """
        # 筛选该球队参与的比赛
        team_matches = []
        for match in matches:
            if match.home_team == team_name or match.away_team == team_name:
                team_matches.append(match)
                
        # 按日期排序，取最近的比赛
        team_matches.sort(key=lambda x: x.date, reverse=True)
        recent_matches = team_matches[:recent_n]
        
        if len(recent_matches) < DATA_CONFIG["min_matches_required"]:
            # 如果数据不足，返回默认值
            return TeamStats(
                team_name=team_name,
                avg_goals_scored=1.0,
                avg_goals_conceded=1.0,
                avg_shots=10.0,
                avg_shots_on_target=3.0,
                avg_possession=50.0,
                avg_pass_success_rate=80.0,
                avg_fouls=12.0,
                avg_corners=5.0,
                avg_yellow_cards=2.0,
                avg_red_cards=0.1,
                total_matches=len(recent_matches)
            )
        
        # 计算各项统计数据
        goals_scored = []
        goals_conceded = []
        shots = []
        shots_on_target = []
        possession = []
        pass_success = []
        fouls = []
        corners = []
        yellow_cards = []
        red_cards = []
        
        for match in recent_matches:
            if match.home_team == team_name:
                # 作为主队
                goals_scored.append(match.home_goals)
                goals_conceded.append(match.away_goals)
                shots.append(match.home_shots)
                shots_on_target.append(match.home_shots_on_target)
                possession.append(match.home_possession)
                pass_success.append(match.home_pass_success)
                fouls.append(match.home_fouls)
                corners.append(match.home_corners)
                yellow_cards.append(match.home_yellow_cards)
                red_cards.append(match.home_red_cards)
            else:
                # 作为客队
                goals_scored.append(match.away_goals)
                goals_conceded.append(match.home_goals)
                shots.append(match.away_shots)
                shots_on_target.append(match.away_shots_on_target)
                possession.append(match.away_possession)
                pass_success.append(match.away_pass_success)
                fouls.append(match.away_fouls)
                corners.append(match.away_corners)
                yellow_cards.append(match.away_yellow_cards)
                red_cards.append(match.away_red_cards)
        
        # 计算平均值
        stats = TeamStats(
            team_name=team_name,
            avg_goals_scored=np.mean(goals_scored),
            avg_goals_conceded=np.mean(goals_conceded),
            avg_shots=np.mean(shots),
            avg_shots_on_target=np.mean(shots_on_target),
            avg_possession=np.mean(possession),
            avg_pass_success_rate=np.mean(pass_success),
            avg_fouls=np.mean(fouls),
            avg_corners=np.mean(corners),
            avg_yellow_cards=np.mean(yellow_cards),
            avg_red_cards=np.mean(red_cards),
            total_matches=len(recent_matches)
        )
        
        # 缓存结果
        cache_key = f"{team_name}_{recent_n}"
        self.team_stats_cache[cache_key] = stats
        
        return stats
    
    def predict_team_goals(self, team_stats: TeamStats, is_home: bool = True) -> float:
        """
        预测单队进球数
        
        Args:
            team_stats: 球队统计数据
            is_home: 是否为主队
            
        Returns:
            float: 预测进球数
        """
        # 核心公式：(场均进球 + 对手场均失球)/2
        base_goals = (team_stats.avg_goals_scored + team_stats.avg_goals_conceded) / 2
        
        # 主场优势修正
        if is_home:
            base_goals *= self.coefficients["home_advantage"]
        
        # 限制在合理范围内
        min_goal, max_goal = DATA_CONFIG["goal_limits"]
        final_goals = np.clip(base_goals, min_goal, max_goal)
        
        return round(final_goals, 1)
    
    def predict_total_goals(self, home_stats: TeamStats, away_stats: TeamStats) -> float:
        """
        预测全场总进球数
        
        Args:
            home_stats: 主队统计数据
            away_stats: 客队统计数据
            
        Returns:
            float: 总进球预测
        """
        home_goals = self.predict_team_goals(home_stats, is_home=True)
        away_goals = self.predict_team_goals(away_stats, is_home=False)
        total_goals = home_goals + away_goals
        
        # 联赛总进球基线修正
        baseline_ratio = self.coefficients["goal_baseline"] / 2.5  # 2.5为基准值
        adjusted_total = total_goals * baseline_ratio
        
        min_goal, max_goal = DATA_CONFIG["goal_limits"]
        return round(np.clip(adjusted_total, min_goal * 2, max_goal * 2), 1)
    
    def predict_corners(self, match_data: MatchData, home_stats: TeamStats, 
                       away_stats: TeamStats) -> Dict[str, float]:
        """
        预测角球数
        
        Args:
            match_data: 比赛基础数据
            home_stats: 主队统计数据
            away_stats: 客队统计数据
            
        Returns:
            Dict: {"home": 主队角球, "away": 客队角球, "total": 总数}
        """
        # 角球核心逻辑：控球率差 + 射门数/4 + 球队角球基线
        possession_diff = match_data.home_possession - match_data.away_possession
        shot_factor = (match_data.home_shots + match_data.away_shots) / 4
        
        # 主队角球预测
        home_corners = (home_stats.avg_corners + 
                       (possession_diff * 0.1) +  # 控球率影响系数
                       (shot_factor * 0.3))       # 射门影响系数
        
        # 客队角球预测
        away_corners = (away_stats.avg_corners - 
                       (possession_diff * 0.1) + 
                       (shot_factor * 0.3))
        
        # 确保非负值
        home_corners = max(home_corners, 0)
        away_corners = max(away_corners, 0)
        
        # 联赛角球基线修正
        total_corners = home_corners + away_corners
        baseline_ratio = self.coefficients["corner_baseline"] / 9.0
        adjusted_total = total_corners * baseline_ratio
        
        min_corner, max_corner = DATA_CONFIG["corner_limits"]
        adjusted_total = np.clip(adjusted_total, min_corner, max_corner)
        
        # 按比例分配回各队
        if total_corners > 0:
            home_ratio = home_corners / total_corners
            away_ratio = away_corners / total_corners
            home_corners = adjusted_total * home_ratio
            away_corners = adjusted_total * away_ratio
        else:
            home_corners = away_corners = adjusted_total / 2
        
        return {
            "home": round(home_corners, 1),
            "away": round(away_corners, 1),
            "total": round(adjusted_total, 1)
        }
    
    def predict_yellow_cards(self, match_data: MatchData, home_stats: TeamStats, 
                            away_stats: TeamStats) -> Dict[str, float]:
        """
        预测黄牌数（包括红牌折算）
        
        Args:
            match_data: 比赛基础数据
            home_stats: 主队统计数据
            away_stats: 客队统计数据
            
        Returns:
            Dict: {"home": 主队黄牌, "away": 客队黄牌, "total": 总数}
        """
        # 黄牌核心逻辑：球队黄牌基线 + 犯规数×转换系数 + 红牌折算
        home_base_yellow = home_stats.avg_yellow_cards
        away_base_yellow = away_stats.avg_yellow_cards
        
        # 犯规转换为黄牌
        home_foul_yellow = match_data.home_fouls * self.coefficients["foul_to_yellow"]
        away_foul_yellow = match_data.away_fouls * self.coefficients["foul_to_yellow"]
        
        # 红牌折算（每张红牌相当于2张黄牌）
        home_red_penalty = home_stats.avg_red_cards * self.coefficients["red_card_penalty"]
        away_red_penalty = away_stats.avg_red_cards * self.coefficients["red_card_penalty"]
        
        # 计算各队黄牌预测
        home_yellow = home_base_yellow + home_foul_yellow + home_red_penalty
        away_yellow = away_base_yellow + away_foul_yellow + away_red_penalty
        
        # 联赛黄牌基线修正
        total_yellow = home_yellow + away_yellow
        baseline_ratio = self.coefficients["yellow_card_baseline"] / 4.5
        adjusted_total = total_yellow * baseline_ratio
        
        min_yellow, max_yellow = DATA_CONFIG["yellow_card_limits"]
        adjusted_total = np.clip(adjusted_total, min_yellow, max_yellow)
        
        # 按比例分配回各队
        if total_yellow > 0:
            home_ratio = home_yellow / total_yellow
            away_ratio = away_yellow / total_yellow
            home_yellow = adjusted_total * home_ratio
            away_yellow = adjusted_total * away_ratio
        else:
            home_yellow = away_yellow = adjusted_total / 2
        
        return {
            "home": round(home_yellow, 1),
            "away": round(away_yellow, 1),
            "total": round(adjusted_total, 1)
        }
    
    def predict_match(self, match_data: MatchData, historical_matches: List[MatchData]) -> PredictionResult:
        """
        对单场比赛进行全面预测
        
        Args:
            match_data: 待预测的比赛数据
            historical_matches: 历史比赛数据
            
        Returns:
            PredictionResult: 预测结果
        """
        # 计算两队统计数据
        home_stats = self.calculate_team_stats(historical_matches, match_data.home_team)
        away_stats = self.calculate_team_stats(historical_matches, match_data.away_team)
        
        # 进行各项预测
        home_goals = self.predict_team_goals(home_stats, is_home=True)
        away_goals = self.predict_team_goals(away_stats, is_home=False)
        total_goals = self.predict_total_goals(home_stats, away_stats)
        
        corners_pred = self.predict_corners(match_data, home_stats, away_stats)
        yellow_pred = self.predict_yellow_cards(match_data, home_stats, away_stats)
        
        # 构造预测结果
        result = PredictionResult(
            home_team_goals=home_goals,
            away_team_goals=away_goals,
            total_goals=total_goals,
            home_corners=corners_pred["home"],
            away_corners=corners_pred["away"],
            total_corners=corners_pred["total"],
            home_yellow_cards=yellow_pred["home"],
            away_yellow_cards=yellow_pred["away"],
            total_yellow_cards=yellow_pred["total"]
        )
        
        return result
    
    def batch_predict(self, matches_to_predict: List[MatchData], 
                     historical_matches: List[MatchData]) -> List[PredictionResult]:
        """
        批量预测多场比赛
        
        Args:
            matches_to_predict: 待预测的比赛列表
            historical_matches: 历史比赛数据
            
        Returns:
            List[PredictionResult]: 预测结果列表
        """
        results = []
        for match in matches_to_predict:
            prediction = self.predict_match(match, historical_matches)
            results.append(prediction)
        return results