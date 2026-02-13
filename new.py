import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
# 读取初始数据集
# 尝试不同的编码格式
try:
    df = pd.read_csv('football.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv('football.csv', encoding='gbk')
    except UnicodeDecodeError:
        print("无法解析文件，请尝试其他编码格式")

print(df)
# 虚构的假设数据
# data = {
#     'homeAttack': [5, 4, 6, 3],
#     'homeDefense': [2, 3, 4, 2],
#     'homeInjury': [0, 1, 0, 0],
#     'homeHistory_corner_kicks': [5, 7, 8, 3],
#     'visitAttack': [4, 5, 5, 4],
#     'visitDefense': [3, 2, 3, 2],
#     'visitInjury': [0, 0, 1, 0],
#     'visitHistory_corner_kicks': [10, 5, 6, 3],
#     'weatherFactors': [1, 2, 1, 2],
#     'Pre_Pre_corner_kicks': [6, 5, 4, 7]
# }
#
# df = pd.DataFrame(data)   # data转行为数据框

# 定义自变量和因变量
X = df[['homeAttack', 'homeDefense', 'homeInjury', 'homeHistory_corner_kicks',
        'visitAttack', 'visitDefense', 'visitInjury', 'visitHistory_corner_kicks',
        'weatherFactors']]
y = df['Pre_Pre_corner_kicks']

# 建立线性回归模型
model = LinearRegression()
model.fit(X, y)   # 训练回归模型

# 模拟持续更新模型
for i in range(10):  # 示例进行10次更新
    new_data = pd.read_csv('football.csv'.format(i))
    new_X = new_data[['homeAttack', 'homeDefense', 'homeInjury', 'homeHistory_corner_kicks',
                      'visitAttack', 'visitDefense', 'visitInjury', 'visitHistory_corner_kicks',
                      'weatherFactors']]
    new_y = new_data['Pre_Pre_corner_kicks']

    # 更新模型
    model.fit(new_X, new_y)

    # 预测并输出结果
    predicted_corner_kicks = model.predict(new_X)
    print('第{}次预测角球数量：'.format(i + 1), predicted_corner_kicks)

# 可视化最终预测结果
plt.figure()
plt.plot(predicted_corner_kicks, marker='o', label='Predicted Corner Kicks')
plt.xlabel('Match Index')
plt.ylabel('Corner Kicks')
plt.title('Final Predicted Corner Kicks for the New Match')
plt.legend()
plt.show()