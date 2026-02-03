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

# 初始化 LaTeX 表格存储
latex_tables = {}

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

    # 将季度列扩展为字符串格式
    quarterly_data.columns = quarterly_data.columns.astype(str)

    # 添加仓库名称列
    quarterly_data["repository"] = repo

    # 保存 LaTeX 表格到字典
    latex_tables[repo] = quarterly_data.to_latex(
        caption=f"Quarterly Commit Counts for Top Contributors ({repo})",
        label=f"tab:{repo.replace('/', '_')}",
        index=True,
        header=True,
        bold_rows=True
    )

# 打印所有 LaTeX 表格
for repo, latex_table in latex_tables.items():
    print(f"% Table for repository: {repo}")
    print(latex_table)
    print("\n")

# 关闭数据库连接
client.close()