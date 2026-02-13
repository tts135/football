import pandas as pd
import os
import matplotlib.pyplot as plt

# 定义存储数据的文件路径
OUTPUT_FILE  = 'bothTeamData.csv'
# 定义常量表示要筛选的最近比赛次数
NUM_MATCHES = 10

# 如果文件已存在，先删除旧文件
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# 尝试不同的编码格式
try:
    df = pd.read_csv('FootballData.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv('FootballData.csv', encoding='gbk')
    except UnicodeDecodeError:
        print("无法解析文件，请尝试其他编码格式")

# 提取切尔西和曼城队伍最近的比赛数据
# 手动输入要筛选的队伍名称
# team1 = input("请输入第一个队伍的名称：")
# team2 = input("请输入第二个队伍的名称：")
team1 = '狼队'
team2 = '拉齐奥'

# 从狼队的比赛记录中取最近的十场比赛
matches_team1 = df[(df['主队'] == team1) | (df['客队'] == team1)].tail(NUM_MATCHES)
# 从拉齐奥的比赛记录中取最近的十场比赛
matches_team2 = df[(df['主队'] == team2) | (df['客队'] == team2)].tail(NUM_MATCHES)
# 合并两支队伍的最近十场比赛记录
# 输出各队最近比赛次数
print("狼队最近比赛次数：", len(matches_team1))
print("拉齐奥最近比赛次数：", len(matches_team2))
filtered_matches = pd.concat([matches_team1, matches_team2]).reset_index(drop=True)
# 将日期数据统一转换为日期格式
# filtered_matches['日期'] = pd.to_datetime(filtered_matches['日期'], format='%Y/%m/%d %H:%M:%S', errors='coerce')
# 根据日期排序
# filtered_matches_sorted = filtered_matches.sort_values(by='日期', ascending=False)

filtered_matches_sorted = filtered_matches.sort_values(by='日期', ascending=False, ignore_index=True)
# 将数据输出到Excel表格
print(filtered_matches_sorted)
# 调整Pandas的显示选项，确保日期内容正确显示
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
filtered_matches_sorted.to_csv(OUTPUT_FILE, index=False)


teams = ['team1', 'team2']
locations = ['Home', 'Away']

goals = [[10, 8], [12, 7]]
corners = [[6, 4], [5, 3]]

fig, ax = plt.subplots(2, 2, figsize=(10, 8))

for i in range(2):
    ax[i, 0].bar(locations, goals[i], color=['blue', 'orange'])
    ax[i, 0].set_title(f'{teams[i]} Goals')
    ax[i, 0].set_ylim(0, 10)

    ax[i, 1].bar(locations, corners[i], color=['green', 'red'])
    ax[i, 1].set_title(f'{teams[i]} Corners')
    ax[i, 1].set_ylim(0, 20)

plt.tight_layout()
plt.show()