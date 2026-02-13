#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本 - 不依赖外部库
验证基本功能是否正常
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """测试基本模块导入"""
    print("=== 测试基本模块导入 ===")
    
    try:
        # 测试配置模块（不依赖外部库）
        from src.config.league_coefficients import LEAGUE_COEFFICIENTS, DEFAULT_LEAGUE
        print("✓ 配置模块导入成功")
        print(f"  默认联赛: {DEFAULT_LEAGUE}")
        print(f"  可用联赛数: {len(LEAGUE_COEFFICIENTS)}")
        
        # 测试数据模型
        from src.models.data_models import TeamStats, MatchData
        print("✓ 数据模型导入成功")
        
        # 创建测试数据
        test_stats = TeamStats(
            team_name="测试球队",
            avg_goals_scored=1.5,
            avg_goals_conceded=1.2,
            avg_shots=12.0,
            avg_shots_on_target=4.0,
            avg_possession=55.0,
            avg_pass_success_rate=82.0,
            avg_fouls=11.0,
            avg_corners=5.5,
            avg_yellow_cards=1.8,
            avg_red_cards=0.1,
            total_matches=10
        )
        print("✓ 数据模型实例化成功")
        
        test_match = MatchData(
            match_id="TEST001",
            league="中超",
            date="2024-01-01",
            home_team="主队",
            away_team="客队",
            home_goals=2,
            away_goals=1,
            home_shots=15,
            away_shots=12,
            home_shots_on_target=6,
            away_shots_on_target=4,
            home_possession=58.0,
            away_possession=42.0,
            home_pass_success=85.0,
            away_pass_success=78.0,
            home_fouls=10,
            away_fouls=14,
            home_yellow_cards=2,
            away_yellow_cards=3,
            home_corners=6,
            away_corners=4,
            home_red_cards=0,
            away_red_cards=0
        )
        print("✓ 比赛数据模型实例化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_prediction_logic():
    """测试简单的预测逻辑"""
    print("\n=== 测试简单预测逻辑 ===")
    
    try:
        # 模拟预测逻辑（不使用复杂模块）
        def simple_goal_prediction(home_stats_avg, away_stats_avg, home_advantage=1.15):
            """简化的进球预测"""
            base_home = (home_stats_avg + (2.6 - away_stats_avg)) / 2  # 2.6是中超场均进球
            base_away = (away_stats_avg + (2.6 - home_stats_avg)) / 2
            home_pred = base_home * home_advantage
            away_pred = base_away
            return round(home_pred, 1), round(away_pred, 1)
        
        # 测试数据
        home_attack = 1.8  # 主队场均进球
        away_defense = 1.1  # 客队场均失球
        away_attack = 1.2  # 客队场均进球
        home_defense = 1.4  # 主队场均失球
        
        home_goals, away_goals = simple_goal_prediction(
            (home_attack + away_defense) / 2,
            (away_attack + home_defense) / 2
        )
        
        print("✓ 简单预测逻辑测试成功")
        print(f"  预测比分: {home_goals} - {away_goals}")
        
        # 验证结果合理性
        assert 0 <= home_goals <= 5, "主队进球预测不合理"
        assert 0 <= away_goals <= 5, "客队进球预测不合理"
        print("✓ 预测结果验证通过")
        
        return True
        
    except Exception as e:
        print(f"✗ 预测逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n=== 测试文件结构 ===")
    
    required_files = [
        'src/__init__.py',
        'src/models/__init__.py',
        'src/models/data_models.py',
        'src/data/__init__.py',
        'src/data/data_processor.py',
        'src/predictors/__init__.py',
        'src/predictors/football_predictor.py',
        'src/trainers/__init__.py',
        'src/trainers/baseline_trainer.py',
        'src/config/__init__.py',
        'src/config/league_coefficients.py',
        'src/main.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("✗ 缺少以下文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("✓ 所有必需文件存在")
        print(f"  共计 {len(required_files)} 个文件")
        return True

def main():
    """主测试函数"""
    print("开始简单系统测试...")
    print("=" * 50)
    
    tests = [
        ("文件结构", test_file_structure),
        ("基本导入", test_basic_imports),
        ("预测逻辑", test_simple_prediction_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} 测试通过")
            else:
                print(f"✗ {test_name} 测试失败")
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 基本系统结构正常！")
        print("\n下一步建议:")
        print("1. 安装pandas和numpy: pip install pandas numpy")
        print("2. 运行完整测试: python test_system.py")
        print("3. 使用主程序: python src/main.py --mode interactive")
        return True
    else:
        print("❌ 系统存在问题，请检查文件结构")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)