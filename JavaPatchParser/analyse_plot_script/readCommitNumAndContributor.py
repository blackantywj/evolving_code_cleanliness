from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['font.family'] = 'Times New Roman'

# 1. 连接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")  # 替换为你的 MongoDB 地址

# 2. 选择数据库
db = client["google"]  # 替换为你的数据库名称

# 3. 选择集合（表格）
collection = db["github_commit"]  # 替换为你的集合名称

# 定义结果存储字典
result = {}

query = {"committer": {"$exists": True}, "author": {"$exists": True}, "release_time": {"$gte": "2022-01-01", "$lte": "2024-12-15"}} 

# 初始化数据存储
data = []

# 遍历符合条件的文档
for doc in collection.find(query):
    repository = doc.get("repository")
    release_time = doc.get("release_time")
    committer = doc.get("committer")
    author = doc.get("author")

    # 确定真实提交者
    if not committer or (committer.get("name") == "web-flow"):
        real_contributor = author.get("name") if author else None
    else:
        real_contributor = committer.get("name")

    if not real_contributor or not repository:
        continue

    # 添加到数据列表
    data.append({
        "repository": repository,
        "contributor": real_contributor,
        "release_time": datetime.strptime(release_time, "%Y-%m-%d")
    })

# 创建 DataFrame
df = pd.DataFrame(data)

# 按 repository 分组
repositories = df["repository"].unique()

# 遍历每个 repository 进行绘图
for repo in repositories:
    repo_df = df[df["repository"] == repo]

    # 统计每位提交者的提交总数
    contributor_totals = repo_df["contributor"].value_counts()

    # 提取前 4 位提交者
    top_contributors = contributor_totals.head(4).index.tolist()

    # 筛选出前 4 位提交者的数据
    top_df = repo_df[repo_df["contributor"].isin(top_contributors)]

    # 按季度统计每位提交者的提交数量
    top_df["quarter"] = top_df["release_time"].dt.to_period("Q")
    quarterly_data = top_df.groupby(["contributor", "quarter"]).size().unstack(fill_value=0)

    # 绘图
    plt.figure(figsize=(10, 6))
    for contributor in top_contributors:
        if contributor in quarterly_data.index:
            plt.plot(
                quarterly_data.columns.astype(str),  # 转换季度为字符串
                quarterly_data.loc[contributor],
                label=contributor,
                marker="o"
            )

    # 图表设置
    plt.title(f"Quarterly Commit Changes of Top 4 Contributors ({repo})")
    plt.xlabel("Quarter")
    plt.ylabel("Number of Commits")
    plt.legend(title="Contributors")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # 显示图表
    plt.savefig(f"readCommitNumAndContributor/{repo.split('/')[0]}_{repo.split('/')[1]}", dpi=600)

# 关闭数据库连接
client.close()

# # 遍历符合条件的集合数据
# for doc in collection.find(query):
#     repository = doc.get("repository")
#     release_time = doc.get("release_time")
#     committer = doc.get("committer")
#     author = doc.get("author")

#     # 确定真实提交者
#     if not committer or (committer.get("name") == "web-flow"):
#         real_contributor = author.get("name") if author else None
#     else:
#         real_contributor = committer.get("name")

#     if not real_contributor:
#         continue  # 跳过无有效提交者的文档

#     # 按仓库和 release_time 统计
#     if repository not in result:
#         result[repository] = {}

#     if release_time not in result[repository]:
#         result[repository][release_time] = {}

#     if real_contributor not in result[repository][release_time]:
#         result[repository][release_time][real_contributor] = 0

#     result[repository][release_time][real_contributor] += 1

# # 打印统计结果
# for repo, releases in result.items():
#     print(f"Repository: {repo}")
#     for release, contributors in releases.items():
#         print(f"  Release Time: {release}")
#         for contributor, count in contributors.items():
#             print(f"    {contributor}: {count} commits")

# # 遍历集合数据
# for doc in collection.find():
#     repository = doc.get("repository")
#     committer = doc.get("committer")
#     author = doc.get("author")

#     # 确定真实提交者
#     if not committer or (committer.get("name") == "web-flow"):
#         real_contributor = author.get("name") if author else None
#     else:
#         real_contributor = committer.get("name")

#     if not real_contributor:
#         continue  # 跳过无有效提交者的文档

#     # 按仓库统计
#     if repository not in result:
#         result[repository] = {}

#     if real_contributor not in result[repository]:
#         result[repository][real_contributor] = 0

#     result[repository][real_contributor] += 1

# # 打印统计结果
# for repo, contributors in result.items():
#     print(f"Repository: {repo}")
#     for contributor, count in contributors.items():
#         print(f"  {contributor}: {count} commits")

# # 关闭数据库连接
# client.close()