#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
定义足球比赛相关的数据结构
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json


@dataclass
class TeamStats:
    """球队历史统计数据（近N场均值）"""
    team_name: str                    # 球队名称
    avg_goals_scored: float          # 场均进球（进攻）
    avg_goals_conceded: float        # 场均失球（防守）
    avg_shots: float                 # 场均射门数
    avg_shots_on_target: float       # 场均射正数
    avg_possession: float            # 场均控球率
    avg_pass_success_rate: float     # 场均传球成功率
    avg_fouls: float                 # 场均犯规数
    avg_corners: float               # 场均角球数
    avg_yellow_cards: float          # 场均黄牌数
    avg_red_cards: float             # 场均红牌数
    total_matches: int               # 统计的比赛场数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'team_name': self.team_name,
            'avg_goals_scored': self.avg_goals_scored,
            'avg_goals_conceded': self.avg_goals_conceded,
            'avg_shots': self.avg_shots,
            'avg_shots_on_target': self.avg_shots_on_target,
            'avg_possession': self.avg_possession,
            'avg_pass_success_rate': self.avg_pass_success_rate,
            'avg_fouls': self.avg_fouls,
            'avg_corners': self.avg_corners,
            'avg_yellow_cards': self.avg_yellow_cards,
            'avg_red_cards': self.avg_red_cards,
            'total_matches': self.total_matches
        }


@dataclass
class MatchData:
    """单场比赛基础数据"""
    match_id: str                    # 比赛ID
    league: str                      # 联赛名
    date: str                        # 比赛日期
    home_team: str                   # 主队
    away_team: str                   # 客队
    home_goals: int                  # 主队进球数
    away_goals: int                  # 客队进球数
    home_shots: int                  # 主队射门数
    away_shots: int                  # 客队射门数
    home_shots_on_target: int        # 主队射正数
    away_shots_on_target: int        # 客队射正数
    home_possession: float           # 主队控球率（0-100）
    away_possession: float           # 客队控球率（0-100）
    home_pass_success: float         # 主队传球成功率（0-100）
    away_pass_success: float         # 客队传球成功率（0-100）
    home_fouls: int                  # 主队犯规数
    away_fouls: int                  # 客队犯规数
    home_yellow_cards: int           # 主队黄牌数
    away_yellow_cards: int           # 客队黄牌数
    home_corners: int                # 主队角球数
    away_corners: int                # 客队角球数
    home_red_cards: int              # 主队红牌数
    away_red_cards: int              # 客队红牌数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'match_id': self.match_id,
            'league': self.league,
            'date': self.date,
            'home_team': self.home_team,
            'away_team': self.away_team,
            'home_goals': self.home_goals,
            'away_goals': self.away_goals,
            'home_shots': self.home_shots,
            'away_shots': self.away_shots,
            'home_shots_on_target': self.home_shots_on_target,
            'away_shots_on_target': self.away_shots_on_target,
            'home_possession': self.home_possession,
            'away_possession': self.away_possession,
            'home_pass_success': self.home_pass_success,
            'away_pass_success': self.away_pass_success,
            'home_fouls': self.home_fouls,
            'away_fouls': self.away_fouls,
            'home_yellow_cards': self.home_yellow_cards,
            'away_yellow_cards': self.away_yellow_cards,
            'home_corners': self.home_corners,
            'away_corners': self.away_corners,
            'home_red_cards': self.home_red_cards,
            'away_red_cards': self.away_red_cards
        }


@dataclass
class PredictionResult:
    """预测结果数据结构"""
    home_team_goals: float           # 主队进球预测
    away_team_goals: float           # 客队进球预测
    total_goals: float               # 总进球预测
    home_corners: float              # 主队角球预测
    away_corners: float              # 客队角球预测
    total_corners: float             # 总角球预测
    home_yellow_cards: float         # 主队黄牌预测
    away_yellow_cards: float         # 客队黄牌预测
    total_yellow_cards: float        # 总黄牌预测
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典格式"""
        return {
            'home_team_goals': self.home_team_goals,
            'away_team_goals': self.away_team_goals,
            'total_goals': self.total_goals,
            'home_corners': self.home_corners,
            'away_corners': self.away_corners,
            'total_corners': self.total_corners,
            'home_yellow_cards': self.home_yellow_cards,
            'away_yellow_cards': self.away_yellow_cards,
            'total_yellow_cards': self.total_yellow_cards
        }
    
    def __str__(self) -> str:
        """格式化输出预测结果"""
        return f"""预测结果:
主队进球: {self.home_team_goals:.1f}
客队进球: {self.away_team_goals:.1f}
总进球数: {self.total_goals:.1f}
主队角球: {self.home_corners:.1f}
客队角球: {self.away_corners:.1f}
总角球数: {self.total_corners:.1f}
主队黄牌: {self.home_yellow_cards:.1f}
客队黄牌: {self.away_yellow_cards:.1f}
总黄牌数: {self.total_yellow_cards:.1f}"""


@dataclass
class RawMatchData:
    """原始比赛数据结构（用于解析JSON数据）"""
    match_id: str
    league_name: str
    date: str
    home_team: str
    away_team: str
    half_time_score: str = ""
    full_time_score: str = ""
    shots: str = "0/0"
    shots_on_target: str = "0/0"
    possession: str = "0%/0%"
    pass_success: str = "0%/0%"
    fouls: str = "0/0"
    yellow_cards: str = "0/0"
    corners: str = "0/0"
    half_corners: str = "0/0"
    red_cards: str = "0/0"
    shots_on_woodwork: str = "0/0"