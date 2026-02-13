#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
足球数据分析包初始化文件
"""

__version__ = "1.0.0"
__author__ = "Football Analysis Team"

# 导出主要类和函数
from .models.data_models import TeamStats, MatchData, PredictionResult, RawMatchData

# 条件导入依赖外部库的模块
try:
    from .data.data_processor import DataProcessor, process_football_data
    from .predictors.football_predictor import FootballPredictor
    from .trainers.baseline_trainer import BaselineTrainer, train_baselines_from_directories
    from .main import FootballAnalysisSystem
    _HAS_EXTERNAL_DEPS = True
except ImportError:
    # 当缺少pandas等依赖时，只导出基础模块
    _HAS_EXTERNAL_DEPS = False
    DataProcessor = None
    process_football_data = None
    FootballPredictor = None
    BaselineTrainer = None
    train_baselines_from_directories = None
    FootballAnalysisSystem = None

__all__ = [
    'TeamStats',
    'MatchData', 
    'PredictionResult',
    'RawMatchData',
]

# 只有在有外部依赖时才导出相关模块
if _HAS_EXTERNAL_DEPS:
    __all__.extend([
        'DataProcessor',
        'process_football_data',
        'FootballPredictor',
        'BaselineTrainer',
        'train_baselines_from_directories',
        'FootballAnalysisSystem'
    ])
else:
    print("警告: 缺少pandas/numpy依赖，部分功能不可用。请运行 'pip install pandas numpy'")