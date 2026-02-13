#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
验证重构后的足球数据分析系统是否正常工作
"""

import sys
import os

# 确保使用正确的Python路径
print(f"使用Python解释器: {sys.executable}")

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试模块导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from src.models.data_models import TeamStats, MatchData, PredictionResult
        print("✓ 数据模型导入成功")
        
        from src.data.data_processor import DataProcessor
        print("✓ 数据处理模块导入成功")
        
        from src.predictors.football_predictor import FootballPredictor
        print("✓ 预测模块导入成功")
        
        from src.trainers.baseline_trainer import BaselineTrainer
        print("✓ 训练模块导入成功")
        
        from src.config.league_coefficients import LEAGUE_COEFFICIENTS
        print("✓ 配置模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_data_processing():
    """测试数据处理功能"""
    print("\n=== 测试数据处理功能 ===")
    
    try:
        from src.data.data_processor import process_football_data
        
        # 测试处理现有数据
        data_dirs = ['2021', '2023']
        matches = process_football_data(data_dirs, "test_processed_data.csv")
        
        if matches:
            print(f"✓ 成功处理 {len(matches)} 场比赛数据")
            print(f"  示例比赛: {matches[0].home_team} vs {matches[0].away_team}")
            return True
        else:
            print("✗ 未找到有效数据")
            return False
            
    except Exception as e:
        print(f"✗ 数据处理测试失败: {e}")
        return False

def test_prediction():
    """测试预测功能"""
    print("\n=== 测试预测功能 ===")
    
    try:
        from src.data.data_processor import process_football_data
        from src.predictors.football_predictor import FootballPredictor
        
        # 加载数据
        matches = process_football_data(['2021', '2023'])
        if not matches:
            print("✗ 无数据可用于预测测试")
            return False
        
        # 创建预测器
        predictor = FootballPredictor(league="中超")
        print("✓ 预测器创建成功")
        
        # 测试单场比赛预测
        sample_match = matches[0]  # 使用第一场比赛作为示例
        prediction = predictor.predict_match(sample_match, matches[:50])  # 使用前50场比赛作为历史数据
        
        print("✓ 预测功能测试成功")
        print(f"  预测结果: {prediction}")
        return True
        
    except Exception as e:
        print(f"✗ 预测功能测试失败: {e}")
        return False

def test_training():
    """测试训练功能"""
    print("\n=== 测试训练功能 ===")
    
    try:
        from src.data.data_processor import process_football_data
        from src.trainers.baseline_trainer import BaselineTrainer
        
        # 加载数据
        matches = process_football_data(['2021', '2023'])
        if len(matches) < 10:
            print("✗ 数据量不足进行训练测试")
            return False
        
        # 训练基线参数
        trainer = BaselineTrainer()
        baselines = trainer.train_from_matches(matches[:100])  # 使用前100场比赛
        
        if baselines:
            print("✓ 训练功能测试成功")
            print(f"  训练的联赛数: {len(baselines)}")
            for league, params in list(baselines.items())[:2]:  # 显示前两个联赛
                print(f"  {league}: 总进球基线={params['goal_baseline']:.2f}")
            return True
        else:
            print("✗ 训练未产生有效结果")
            return False
            
    except Exception as e:
        print(f"✗ 训练功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试足球数据分析系统...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("数据处理", test_data_processing),
        ("预测功能", test_prediction),
        ("训练功能", test_training)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)