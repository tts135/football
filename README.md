# 足球数据分析预测系统

## 项目概述

这是一个基于统计基线法和联赛特征修正的足球数据分析预测系统，能够预测比赛的进球数、角球数和黄牌数等关键指标。

## 项目结构

```
football/
├── src/                    # 源代码目录
│   ├── config/            # 配置文件
│   │   └── league_coefficients.py  # 联赛系数配置
│   ├── data/              # 数据处理模块
│   │   └── data_processor.py       # 数据解析和处理
│   ├── models/            # 数据模型
│   │   └── data_models.py          # 数据结构定义
│   ├── predictors/        # 预测模块
│   │   └── football_predictor.py   # 核心预测算法
│   ├── trainers/          # 训练模块
│   │   └── baseline_trainer.py     # 基线参数训练
│   └── main.py            # 主程序入口
├── 2021/                  # 2021年原始数据
├── 2023/                  # 2023年原始数据
├── simple_test.py         # 简单测试脚本
├── test_system.py         # 完整测试脚本
└── README.md              # 本文件
```

## 功能特性

### 核心预测功能
- **进球数预测**: 基于球队攻防统计数据和主场优势
- **角球数预测**: 结合控球率、射门数和历史角球数据
- **黄牌数预测**: 考虑犯规数、历史黄牌记录和红牌折算
- **多联赛支持**: 内置中超、意甲、英超、西甲、德甲系数

### 数据处理能力
- **JSON数据解析**: 自动解析原始爬虫数据
- **数据清洗**: 处理缺失值和异常数据
- **统计计算**: 自动生成球队历史统计数据

### 模型训练
- **基线参数训练**: 基于历史数据自动计算联赛特征
- **交叉验证**: 评估模型预测准确性
- **参数优化**: 自动调整预测系数

## 安装和使用

### 1. 环境准备

```bash
# 安装必要依赖
pip install pandas numpy

# 或者如果使用conda
conda install pandas numpy
```

### 2. 快速开始

```bash
# 运行简单测试（不需要外部依赖）
python simple_test.py

# 运行完整测试
python test_system.py

# 启动交互式预测
python src/main.py --mode interactive

# 训练基线参数
python src/main.py --mode train

# 预测特定比赛
python src/main.py --mode predict --home-team "成都蓉城" --away-team "北京国安" --league "中超"
```

### 3. 使用示例

```python
from src.predictors.football_predictor import FootballPredictor
from src.data.data_processor import process_football_data

# 加载历史数据
matches = process_football_data(['2021', '2023'])

# 创建预测器
predictor = FootballPredictor(league="中超")

# 预测比赛
result = predictor.predict_single_match("成都蓉城", "北京国安")
print(result)
```

## 预测算法原理

### 进球数预测
```
基础公式: (球队场均进球 + 对手场均失球) / 2
主场修正: 基础值 × 主场优势系数
联赛修正: 调整至联赛平均水平
```

### 角球数预测
```
核心逻辑: 控球率差异 + 射门数因子 + 球队角球基线
主场优势: 主队控球率优势带来额外角球
联赛修正: 按联赛平均角球数调整
```

### 黄牌数预测
```
基础构成: 球队历史黄牌 + 犯规转黄牌 + 红牌折算
转换系数: 每5次犯规 ≈ 1张黄牌
联赛修正: 考虑不同联赛的执法尺度
```

## 配置说明

### 联赛系数配置
在 `src/config/league_coefficients.py` 中定义各联赛的基础参数：

```python
LEAGUE_COEFFICIENTS = {
    "中超": {
        "goal_baseline": 2.6,      # 场均总进球
        "corner_baseline": 9.5,    # 场均角球总数
        "yellow_card_baseline": 4.2,  # 场均黄牌总数
        "home_advantage": 1.15,    # 主场优势系数
        "foul_to_yellow": 0.18,    # 犯规转黄牌系数
        "red_card_penalty": 2.0    # 红牌折算
    }
    # ... 其他联赛
}
```

### 数据处理配置
```python
DATA_CONFIG = {
    "recent_matches_window": 10,   # 使用最近10场比赛统计
    "min_matches_required": 3,     # 最少需要3场比赛
    "goal_limits": (0.0, 5.0),     # 进球数合理范围
    # ... 其他配置
}
```

## 性能评估

系统提供交叉验证功能评估预测准确性：

```bash
# 5折交叉验证
python src/main.py --mode evaluate --k-folds 5
```

评估指标包括：
- **MAE**: 平均绝对误差
- **RMSE**: 均方根误差  
- **准确率**: 胜平负方向判断准确率

## 扩展开发

### 添加新联赛
1. 在 `league_coefficients.py` 中添加联赛配置
2. 准备该联赛的历史数据
3. 运行训练生成基线参数

### 自定义预测逻辑
```python
class CustomPredictor(FootballPredictor):
    def predict_team_goals(self, team_stats, is_home=True):
        # 自定义进球预测逻辑
        pass
```

### 集成机器学习
系统预留了机器学习扩展接口，可方便集成：
- 线性回归模型
- XGBoost/LightGBM
- 深度学习模型

## 注意事项

1. **数据质量**: 确保输入数据格式正确
2. **样本量**: 建议至少50场比赛数据用于训练
3. **时效性**: 定期更新基线参数以适应联赛变化
4. **局限性**: 统计方法无法预测突发事件影响

## 故障排除

常见问题及解决方案：

1. **ModuleNotFoundError**: 安装缺失的依赖包
2. **数据解析错误**: 检查JSON数据格式是否标准
3. **预测结果异常**: 确认球队名称拼写正确
4. **内存不足**: 减少处理的数据量或增加系统内存

## 版本历史

- **v1.0.0**: 初始版本，实现基础预测功能
- 支持多联赛预测
- 完整的数据处理流程
- 模型训练和评估功能

## 许可证

本项目仅供学习和研究使用。