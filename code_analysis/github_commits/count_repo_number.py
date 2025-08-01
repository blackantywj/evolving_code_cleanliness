from pymongo import MongoClient
from collections import defaultdict

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库
db = client['github']

# 获取数据库中的所有集合名称
collections = db.list_collection_names()

# 初始化一个字典，用于存储每个集合的 repository 计数
repository_counts = {}

# 遍历每个集合
for collection_name in collections:
    collection = db[collection_name]
    # 初始化一个默认字典用于计数
    repo_count = defaultdict(int)
    # 遍历集合中的每个文档
    for document in collection.find():
        # 获取 repository 字段的值
        repository = document.get('repository')
        if repository:
            # 增加计数
            repo_count[repository] += 1
    # 将计数结果存储到主字典中
    repository_counts[collection_name] = dict(repo_count)

# 输出结果
for collection_name, counts in repository_counts.items():
    print(f"集合 '{collection_name}' 的 repository 计数：")
    for repo, count in counts.items():
        print(f"  仓库 '{repo}': {count} 次")
