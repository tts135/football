#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
足球数据分析Web应用后端
提供API接口和Web页面服务
"""

import sys
import os
from datetime import datetime
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 添加src目录到Python路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.data.data_processor import process_football_data
from src.predictors.football_predictor import FootballPredictor
from src.models.data_models import MatchData

app = Flask(__name__)
CORS(app)

# 全局变量存储数据和预测器
matches_data = []
predictor = None
league_stats = {}

def initialize_system():
    """初始化系统数据"""
    global matches_data, predictor, league_stats
    
    print("正在初始化足球数据分析系统...")
    
    # 加载数据
    try:
        # 使用标准化数据路径
        data_dirs = [
            os.path.join(project_root, 'data', 'raw', '2021'),
            os.path.join(project_root, 'data', 'raw', '2023')
        ]
        matches_data = process_football_data(data_dirs)
        print(f"成功加载 {len(matches_data)} 场比赛数据")
    except Exception as e:
        print(f"数据加载失败: {e}")
        matches_data = []
    
    # 初始化预测器
    predictor = FootballPredictor(league="中超")
    
    # 计算联赛统计信息
    calculate_league_stats()
    
    print("系统初始化完成!")

def calculate_league_stats():
    """计算联赛统计数据"""
    global league_stats
    
    if not matches_data:
        return
    
    # 按联赛分组统计
    league_data = {}
    for match in matches_data:
        league = match.league
        if league not in league_data:
            league_data[league] = []
        league_data[league].append(match)
    
    # 计算各联赛统计信息
    for league, matches in league_data.items():
        total_goals = sum(match.home_goals + match.away_goals for match in matches)
        total_corners = sum(match.home_corners + match.away_corners for match in matches)
        total_yellow = sum(match.home_yellow_cards + match.away_yellow_cards for match in matches)
        
        league_stats[league] = {
            'match_count': len(matches),
            'avg_goals': round(total_goals / len(matches), 2),
            'avg_corners': round(total_corners / len(matches), 2),
            'avg_yellow_cards': round(total_yellow / len(matches), 2),
            'latest_match_date': max(match.date for match in matches)
        }

# 在应用启动时初始化
initialize_system()

@app.route('/')
def index():
    """主页 - 大屏展示界面"""
    return render_template('dashboard.html')

@app.route('/predict')
def predict_page():
    """预测页面"""
    return render_template('predict.html')

@app.route('/api/matches')
def get_matches():
    """获取比赛数据API"""
    try:
        # 返回最新的几场比赛
        latest_matches = sorted(matches_data, key=lambda x: x.date, reverse=True)[:50]
        
        matches_list = []
        for match in latest_matches:
            matches_list.append({
                'id': match.match_id,
                'league': match.league,
                'date': match.date,
                'home_team': match.home_team,
                'away_team': match.away_team,
                'home_goals': match.home_goals,
                'away_goals': match.away_goals,
                'home_corners': match.home_corners,
                'away_corners': match.away_corners,
                'home_yellow_cards': match.home_yellow_cards,
                'away_yellow_cards': match.away_yellow_cards
            })
        
        return jsonify({
            'success': True,
            'data': matches_list,
            'total': len(matches_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/leagues')
def get_leagues():
    """获取联赛统计信息"""
    try:
        return jsonify({
            'success': True,
            'data': league_stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/teams')
def get_teams():
    """获取所有球队列表"""
    try:
        teams = set()
        for match in matches_data:
            teams.add(match.home_team)
            teams.add(match.away_team)
        
        return jsonify({
            'success': True,
            'data': sorted(list(teams))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/team_history/<team_name>')
def get_team_history(team_name):
    """获取球队最近比赛历史数据"""
    try:
        # 查找该球队的所有比赛
        team_matches = []
        for match in matches_data:
            if match.home_team == team_name or match.away_team == team_name:
                # 判断球队在这场比赛中的角色
                is_home = match.home_team == team_name
                team_role = '主场' if is_home else '客场'
                
                # 计算球队的进球和失球
                team_goals = match.home_goals if is_home else match.away_goals
                opponent_goals = match.away_goals if is_home else match.home_goals
                
                # 计算球队的其他统计数据
                team_corners = match.home_corners if is_home else match.away_corners
                opponent_corners = match.away_corners if is_home else match.home_corners
                team_yellow = match.home_yellow_cards if is_home else match.away_yellow_cards
                opponent_yellow = match.away_yellow_cards if is_home else match.home_yellow_cards
                
                # 确定对手和比赛结果
                opponent = match.away_team if is_home else match.home_team
                result = '胜' if team_goals > opponent_goals else ('负' if team_goals < opponent_goals else '平')
                
                team_matches.append({
                    'date': match.date,
                    'league': match.league,
                    'opponent': opponent,
                    'role': team_role,
                    'score': f'{team_goals}-{opponent_goals}',
                    'result': result,
                    'team_goals': team_goals,
                    'opponent_goals': opponent_goals,
                    'team_corners': team_corners,
                    'opponent_corners': opponent_corners,
                    'team_yellow_cards': team_yellow,
                    'opponent_yellow_cards': opponent_yellow,
                    'possession': match.home_possession if is_home else match.away_possession,
                    'shots': match.home_shots if is_home else match.away_shots,
                    'shots_on_target': match.home_shots_on_target if is_home else match.away_shots_on_target
                })
        
        # 按日期排序，取最近5场
        team_matches.sort(key=lambda x: x['date'], reverse=True)
        recent_matches = team_matches[:5]
        
        return jsonify({
            'success': True,
            'team': team_name,
            'matches': recent_matches,
            'total_matches': len(team_matches)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/predict', methods=['POST'])
def predict_match():
    """预测比赛结果API"""
    try:
        data = request.get_json()
        
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        league = data.get('league', '中超')
        
        if not home_team or not away_team:
            return jsonify({'success': False, 'error': '请提供主队和客队名称'})
        
        # 创建虚拟比赛数据用于预测
        mock_match = MatchData(
            match_id="PREDICTION",
            league=league,
            date=datetime.now().strftime("%Y-%m-%d"),
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
        
        # 进行预测
        result = predictor.predict_match(mock_match, matches_data)
        
        return jsonify({
            'success': True,
            'data': {
                'home_team': home_team,
                'away_team': away_team,
                'league': league,
                'prediction': result.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stats')
def get_system_stats():
    """获取系统统计信息"""
    try:
        # 计算各种统计信息
        total_matches = len(matches_data)
        
        # 联赛分布
        league_distribution = {}
        for match in matches_data:
            league = match.league
            league_distribution[league] = league_distribution.get(league, 0) + 1
        
        # 进球统计
        total_goals = sum(match.home_goals + match.away_goals for match in matches_data)
        avg_goals_per_match = round(total_goals / total_matches, 2) if total_matches > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_matches': total_matches,
                'league_distribution': league_distribution,
                'total_goals': total_goals,
                'avg_goals_per_match': avg_goals_per_match,
                'system_status': 'running',
                'last_update': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'matches_loaded': len(matches_data)
    })

if __name__ == '__main__':
    print("启动足球数据分析Web应用...")
    print("访问地址: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)