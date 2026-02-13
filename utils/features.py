import csv
import json
import pandas as pd

# 读取JSON文件并指定编码方式为utf-8
with open('2021/2021-01.json', encoding='utf-8') as file:
    data = json.load(file)


# 初始化空列表用于存储处理后的数据
processed_data = []

# 循环遍历每场比赛
for match in data:
    # 提取比赛信息
    match_id = match.get("比赛id", "")
    league_name = match.get("联赛名", "")
    date = match.get("日期", "")
    home_team = match.get("主队", "")
    away_team = match.get("客队", "")

    # 处理所有字段中包含"/"的数据
    processed_match = {}
    for key, value in match.items():
        if "/" in value:
            values = value.split("/")
            home_value = values[0].strip() if values[0].strip() != "-" else "0"
            away_value = values[1].strip() if values[1].strip() != "-" else "0"
            processed_match[f"主队{key}"] = home_value
            processed_match[f"客队{key}"] = away_value
        else:
            processed_match[key] = value

    # 将比赛信息加入字典
    processed_match["比赛ID"] = match_id
    processed_match["联赛名"] = league_name
    processed_match["日期"] = date
    processed_match["主队"] = home_team
    processed_match["客队"] = away_team

    # 添加处理后的数据到列表
    processed_data.append(processed_match)

# 转换为DataFrame
df = pd.DataFrame(processed_data)
print(df)