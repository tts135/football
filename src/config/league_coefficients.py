#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联赛系数配置文件
定义各大联赛的基础统计参数和修正系数
"""

# 联赛基础修正系数（基于历史数据统计规律）
LEAGUE_COEFFICIENTS = {
    "中超": {
        "goal_baseline": 2.6,      # 场均总进球基线
        "corner_baseline": 9.5,    # 场均角球总数基线
        "yellow_card_baseline": 4.2,  # 场均黄牌总数基线
        "home_advantage": 1.15,    # 主场进球优势系数
        "foul_to_yellow": 0.18,    # 犯规转黄牌系数
        "red_card_penalty": 2.0    # 红牌折算黄牌数
    },
    "意甲": {
        "goal_baseline": 2.5,
        "corner_baseline": 8.5,
        "yellow_card_baseline": 5.5,
        "home_advantage": 1.18,
        "foul_to_yellow": 0.25,
        "red_card_penalty": 2.0
    },
    "英超": {
        "goal_baseline": 2.8,
        "corner_baseline": 10.5,
        "yellow_card_baseline": 5.0,
        "home_advantage": 1.15,
        "foul_to_yellow": 0.22,
        "red_card_penalty": 2.0
    },
    "西甲": {
        "goal_baseline": 2.7,
        "corner_baseline": 9.5,
        "yellow_card_baseline": 4.8,
        "home_advantage": 1.2,
        "foul_to_yellow": 0.18,
        "red_card_penalty": 2.0
    },
    "德甲": {
        "goal_baseline": 3.0,
        "corner_baseline": 9.8,
        "yellow_card_baseline": 4.2,
        "home_advantage": 1.1,
        "foul_to_yellow": 0.15,
        "red_card_penalty": 2.0
    }
}

# 默认联赛（当无法识别时使用）
DEFAULT_LEAGUE = "中超"

# 数据处理相关配置
DATA_CONFIG = {
    "recent_matches_window": 10,   # 计算球队统计数据时使用的最近比赛场数
    "min_matches_required": 3,     # 计算统计值所需的最少比赛场数
    "goal_limits": (0.0, 5.0),     # 进球数预测的合理范围
    "corner_limits": (0.0, 20.0),  # 角球数预测的合理范围
    "yellow_card_limits": (0.0, 10.0)  # 黄牌数预测的合理范围
}