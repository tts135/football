import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import json


# 读取JSON文件并指定编码方式为utf-8
with open('2023/2023-05.json', encoding='utf-8') as file:
    data = json.load(file)


# 初始化空列表用于存储处理后的数据
processed_data = []

for match in data:
    # 提取比赛信息
    match_id = match.get("比赛id", "")
    league_name = match.get("联赛名", "")
    date = match.get("日期", "")
    home_team = match.get("主队", "")
    away_team = match.get("客队", "")

    # 指定要处理的字段列表
    fields_to_process = ["半场", "射门", "射正", "控球率", "传球成功率", "犯规", "黄牌", "角球", "半场角球", "红牌",
                         "射中门框"]

    processed_match = {"比赛ID": match_id, "联赛名": league_name, "日期": date, "主队": home_team, "客队": away_team}

    for field in fields_to_process:
        value = match.get(field, "0/0")

        if "/" in value:
            values = value.split("/")
            home_value = values[0].strip() if values[0].strip() != "-" else "0"
            away_value = values[1].strip() if values[1].strip() != "-" else "0"
            processed_match[f"主队{field}"] = home_value
            processed_match[f"客队{field}"] = away_value
        else:
            processed_match[f"主队{field}"] = "0"
            processed_match[f"客队{field}"] = "0"

    processed_data.append(processed_match)

# 转换为DataFrame
df = pd.DataFrame(processed_data)
# 将数据输出到Excel表格
df.to_csv('FootballData.csv', index=False)

try:
    data = pd.read_csv('FootballData.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        data = pd.read_csv('FootballData.csv', encoding='gbk')
    except UnicodeDecodeError:
        print("无法解析文件，请尝试其他编码格式")

# 划分特征和标签
X = data[['主队控球率', '客队控球率', '主队射门', '客队射门']]
y = data['主队角球']

# 处理缺失值（如果有）
X.fillna(X.mean(), inplace=True)
y.fillna(y.mean(), inplace=True)

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 查看数据集信息
print(data.info())

# 训练随机森林模型
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 预测测试集
predictions = model.predict(X_test)

# 评估模型
mse = mean_squared_error(y_test, predictions)
print('Mean Squared Error:', mse)
