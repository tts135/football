#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成联赛统计信息JSON文件
基于处理后的比赛数据生成league_stats.json
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

def generate_league_stats():
    """生成联赛统计信息"""
    print("=== 生成联赛统计信息 ===")
    
    # 设置路径
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_data_file = os.path.join(project_root, 'data', 'processed', 'matches.csv')
    output_file = os.path.join(project_root, 'data', 'processed', 'league_stats.json')
    
    # 检查数据文件是否存在
    if not os.path.exists(processed_data_file):
        print(f"❌ 数据文件不存在: {processed_data_file}")
        print("请先运行数据处理脚本: python scripts/setup_data.py")
        return
    
    # 读取处理后的数据
    print(f"读取数据文件: {processed_data_file}")
    df = pd.read_csv(processed_data_file, encoding='utf-8-sig')
    
    # 按联赛分组统计
    league_stats = {}
    
    for league in df['league'].unique():
        league_data = df[df['league'] == league]
        
        # 计算各项统计数据
        total_matches = len(league_data)
        
        # 注意：原始数据中比分字段为空，因此总进球数为0
        # 这是数据源的限制，不是程序错误
        total_goals = (league_data['home_goals'] + league_data['away_goals']).sum()
        total_corners = (league_data['home_角球'] + league_data['away_角球']).sum()
        total_yellow_cards = (league_data['home_黄牌'] + league_data['away_黄牌']).sum()
        total_red_cards = (league_data['home_红牌'] + league_data['away_红牌']).sum()
        total_shots = (league_data['home_射门'] + league_data['away_射门']).sum()
        total_shots_on_target = (league_data['home_射正'] + league_data['away_射正']).sum()
        
        # 计算场均数据
        avg_goals = round(total_goals / total_matches, 2) if total_matches > 0 else 0
        avg_corners = round(total_corners / total_matches, 2) if total_matches > 0 else 0
        avg_yellow_cards = round(total_yellow_cards / total_matches, 2) if total_matches > 0 else 0
        avg_red_cards = round(total_red_cards / total_matches, 2) if total_matches > 0 else 0
        avg_shots = round(total_shots / total_matches, 2) if total_matches > 0 else 0
        avg_shots_on_target = round(total_shots_on_target / total_matches, 2) if total_matches > 0 else 0
        
        # 计算进球比例等
        home_wins = len(league_data[league_data['home_goals'] > league_data['away_goals']])
        away_wins = len(league_data[league_data['home_goals'] < league_data['away_goals']])
        draws = len(league_data[league_data['home_goals'] == league_data['away_goals']])
        
        win_rate_home = round(home_wins / total_matches * 100, 1) if total_matches > 0 else 0
        win_rate_away = round(away_wins / total_matches * 100, 1) if total_matches > 0 else 0
        draw_rate = round(draws / total_matches * 100, 1) if total_matches > 0 else 0
        
        # 计算平均控球率（如果存在）
        if 'home_possession' in df.columns and 'away_possession' in df.columns:
            avg_possession_home = round(league_data['home_possession'].mean(), 1) if not league_data['home_possession'].isna().all() else 0
            avg_possession_away = round(league_data['away_possession'].mean(), 1) if not league_data['away_possession'].isna().all() else 0
        else:
            avg_possession_home = avg_possession_away = 0
            
        league_stats[league] = {
            'basic_info': {
                'league_name': league,
                'total_matches': total_matches,
                'date_range': {
                    'earliest': str(league_data['date'].min()) if not league_data['date'].empty else '',
                    'latest': str(league_data['date'].max()) if not league_data['date'].empty else ''
                }
            },
            'scoring_stats': {
                'total_goals': int(total_goals),
                'average_goals_per_match': avg_goals,
                'home_win_rate': win_rate_home,
                'away_win_rate': win_rate_away,
                'draw_rate': draw_rate
            },
            'attacking_stats': {
                'total_shots': int(total_shots),
                'total_shots_on_target': int(total_shots_on_target),
                'average_shots_per_match': avg_shots,
                'average_shots_on_target_per_match': avg_shots_on_target,
                'shot_accuracy_rate': round(avg_shots_on_target / avg_shots * 100, 1) if avg_shots > 0 else 0
            },
            'disciplinary_stats': {
                'total_yellow_cards': int(total_yellow_cards),
                'total_red_cards': int(total_red_cards),
                'average_yellow_cards_per_match': avg_yellow_cards,
                'average_red_cards_per_match': avg_red_cards
            },
            'set_piece_stats': {
                'total_corners': int(total_corners),
                'average_corners_per_match': avg_corners
            },
            'possession_stats': {
                'average_home_possession': avg_possession_home,
                'average_away_possession': avg_possession_away
            }
        }
    
    # 保存到JSON文件
    print(f"保存联赛统计到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(league_stats, f, ensure_ascii=False, indent=2)
    
    # 显示统计摘要
    print("\n=== 联赛统计摘要 ===")
    for league, stats in league_stats.items():
        print(f"{league}:")
        print(f"  - 比赛场次: {stats['basic_info']['total_matches']}")
        print(f"  - 场均进球: {stats['scoring_stats']['average_goals_per_match']}")
        print(f"  - 场均角球: {stats['set_piece_stats']['average_corners_per_match']}")
        print(f"  - 场均黄牌: {stats['disciplinary_stats']['average_yellow_cards_per_match']}")
        print()
    
    print(f"✅ 联赛统计文件已生成: {output_file}")
    return league_stats

if __name__ == "__main__":
    generate_league_stats()