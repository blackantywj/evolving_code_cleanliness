from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['github']  # 替换为你的数据库名
commit_collection = db['github_commit_2022']  # 替换为你的集合名

# 聚合查询
pipeline = [
    {"$group": {
        "_id": "$repository",  # 按 repository 字段分组
        "commit_count": {"$count": {}}  # 统计每个 repository 的 commit 数量
    }}
]

# 执行聚合查询
result = commit_collection.aggregate(pipeline)

# 打印结果
for entry in result:
    print(f"Repository: {entry['_id']}, Commit Count: {entry['commit_count']}")
