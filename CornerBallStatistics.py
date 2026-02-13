import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

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

# 读取处理后的数据文件
df = pd.read_csv('FootballData.csv')

# 获取所有队伍的名称
all_teams = set(df['主队']).union(set(df['客队']))

# 初始化存储数据的字典
team_data = {team: {'主队角球': [], '客队角球': []} for team in all_teams}

# 提取数据并存储到字典中
for index, row in df.iterrows():
    home_team = row['主队']
    away_team = row['客队']

    home_corners = int(row['主队角球'])
    away_corners = int(row['客队角球'])

    team_data[home_team]['主队角球'].append(home_corners)
    team_data[away_team]['客队角球'].append(away_corners)

# 将DataFrame写入CSV文件
# 将字典转换为DataFrame
team_data_df = pd.DataFrame(team_data)

# 将DataFrame写入CSV文件
team_data_df.to_csv('CornerBallStatistics_output.csv')

# # 绘制折线图
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题
font_path = r'E:\PyCharm Community Edition 2023.3.4\res\SimHei.ttf'
# prop = fm.FontProperties(fname=font_path)
#
# plt.figure(figsize=(12, 8))
#
# for team, data in team_data.items():
#     plt.plot(range(len(data['主队角球'])), data['主队角球'], label=f"{team} 主队角球")
#     plt.plot(range(len(data['客队角球'])), data['客队角球'], label=f"{team} 客队角球")
#
# plt.xlabel('比赛次数')
# plt.ylabel('角球数')
# plt.title('各队主客队角球数统计')
# plt.legend()
# plt.grid(True)
# plt.show()


# 用户输入两支队伍的名称
# team1 = input("请输入第一支队伍的名称：")
# team2 = input("请输入第二支队伍的名称：")

team1 = '成都蓉城'
team2 = '北京国安'
#折线图
# plt.figure(figsize=(12, 8))
# # 绘制第一支队伍的角球数据
# plt.plot(range(len(team_data[team1]['主队角球'])), team_data[team1]['主队角球'], label=f"{team1} 主队角球")
# plt.plot(range(len(team_data[team1]['客队角球'])), team_data[team1]['客队角球'], label=f"{team1} 客队角球")
#
# # 绘制第二支队伍的角球数据
# plt.plot(range(len(team_data[team2]['主队角球'])), team_data[team2]['主队角球'], label=f"{team2} 主队角球")
# plt.plot(range(len(team_data[team2]['客队角球'])), team_data[team2]['客队角球'], label=f"{team2} 客队角球")
#
# plt.xlabel('比赛次数')
# plt.ylabel('角球数')
# plt.title(f'{team1}与{team2}主客队角球数统计')
# plt.legend()
# plt.grid(True)
# plt.show()


#柱形图
# 提取两支队伍的角球数据
plt.figure(figsize=(12, 8))

# 绘制第一支队伍的角球数据
plt.bar(range(len(team_data[team1]['主队角球'])), team_data[team1]['主队角球'], label=f"{team1} 主队角球", color='skyblue')
plt.bar(range(len(team_data[team1]['客队角球'])), team_data[team1]['客队角球'], label=f"{team1} 客队角球", color='dodgerblue', alpha=0.5)

# 绘制第二支队伍的角球数据
plt.bar(range(len(team_data[team2]['主队角球'])), team_data[team2]['主队角球'], label=f"{team2} 主队角球", color='salmon')
plt.bar(range(len(team_data[team2]['客队角球'])), team_data[team2]['客队角球'], label=f"{team2} 客队角球", color='tomato', alpha=0.5)

plt.xlabel('比赛次数')
plt.ylabel('角球数')
plt.title(f'{team1}与{team2}每场比赛角球数统计')
plt.legend()
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.show()