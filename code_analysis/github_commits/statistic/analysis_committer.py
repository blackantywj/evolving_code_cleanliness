from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

# 设置字体为 Times New Roman
plt.rcParams['font.family'] = 'Times New Roman'

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['github']
collection = db['github_commit']

'''
- apache/dubbo: 多版本名
- apache/kafka: 多版本
- apache/incubator-seata: 多版本
- apache/flink: 有主分支
- apache/skywalking: 多版本，有主分支 github_commit
- apache/rocketmq: 多版本，main、master、feature都有
- apache/shardingsphere: 只有主分支 ?
- apache/hadoop: 多版本 ?
- apache/pulsar: 多版本，主分支 ?
- apache/druid: 多版本 ?
- apache/zookeeper: 多版本，主分支 github_commit
'''

repository = "apache/flink"

commits = collection.find({"repository": repository, "download": {"$exists": True}})

dataTotal = set()
controlNum = 5
start_time = "2022-01-01"
end_time = "2024-12-15"
# 将字符串的时间转换为 datetime 对象
start_time = datetime.strptime(start_time, "%Y-%m-%d")
end_time = datetime.strptime(end_time, "%Y-%m-%d")

# 初始化一个嵌套字典：committer -> release_time -> datas个数
committer_stats = defaultdict(lambda: defaultdict(int))

# 假设你的提交数据是一个列表，每个元素是一个字典，表示一个提交
for commit in commits:
    datas = commit['datas']
    release_time = datetime.strptime(commit["release_time"], "%Y-%m-%d")  # 假设release_time是字符串格式

    # 如果commit_sha为None，则跳过该提交
    if commit['commit_sha'] is None:
        continue

    # 根据start_time和end_time过滤提交
    if release_time < start_time or release_time > end_time:
        continue

    # 统计committer的提交和datas个数
    committer = commit['committer']['name']
    if committer != 'web-flow':
        committer_stats[committer][release_time] += len(datas)

# # 计算每个committer的总datas数量
# committer_total_datas = {committer: sum(time_stats.values()) for committer, time_stats in committer_stats.items()}

# # 按照总datas数量降序排序，并选取前十个committer
# top_10_committers = sorted(committer_total_datas.items(), key=lambda x: x[1], reverse=True)[:10]

# 计算每个committer的总datas数量，并按总数排序
committer_total_datas = {committer: sum(time_stats.values()) for committer, time_stats in committer_stats.items()}
sorted_committers = sorted(committer_total_datas.items(), key=lambda x: x[1], reverse=True)[:controlNum]

# 获取前10位committer的名字
top_committers = [committer for committer, _ in sorted_committers]

# 绘制前10位committer的提交数据
plt.figure(figsize=(12, 8))

# 为每个前10位committer创建图表
for committer in top_committers:
    time_stats = committer_stats[committer]
    sorted_times = sorted(time_stats.keys())
    datas_counts = [time_stats[time] for time in sorted_times]
    
    # 添加committer的总datas数到label中
    total_datas = committer_total_datas[committer]
    label = f'{committer} ({total_datas})'  # 显示committer名字和总datas数
    
    # 绘制该committer的时间-数据图
    plt.plot(sorted_times, datas_counts, label=label, marker='o')

# 设置图表的标签和标题
plt.xlabel('Release Time')
plt.ylabel('Number of Datas')
plt.title('Top-%d Committers and Their commits Count Over Time' % controlNum)
plt.legend(title='Committers', loc='upper center')

# 格式化时间显示
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("1.png")
# # 输出结果
# print("Commit statistics by committer and release time:")
# for committer, time_stats in committer_stats.items():
#     print(f"\n{committer}:")
#     for release_time, datas_count in sorted(time_stats.items()):
#         print(f"  {release_time.strftime('%Y-%m-%d')}: {datas_count} datas")
        
# # 绘制每个committer的提交数据
# plt.figure(figsize=(10, 6))

# # 为每个committer创建图表
# for committer, time_stats in committer_stats.items():
#     # 排序时间点
#     sorted_times = sorted(time_stats.keys())
#     datas_counts = [time_stats[time] for time in sorted_times]
    
#     # 绘制该committer的时间-数据图
#     plt.plot(sorted_times, datas_counts, label=committer, marker='o')

# # 设置图表的标签和标题
# plt.xlabel('Release Time')
# plt.ylabel('Number of Datas')
# plt.title('Datas Count per Committer Over Time')
# plt.legend(title='Committers')

# # 格式化时间显示
# plt.xticks(rotation=45)
# plt.tight_layout()

# # 显示图表
# plt.savefig("1.png")
# for commit in commits:
#     commitNum += 1
#     datas = commit['datas']
#     release_time = commit["release_time"]
#     if commit['commit_sha'] == None:
#         continue
#     if start_time:
#         if release_time <= start_time:
#             continue
#     if end_time:
#         if release_time >= end_time:
#             continue
#     committer = commit['committer']
    
    