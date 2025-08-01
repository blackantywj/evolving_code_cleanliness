# import random
# import datetime
# from pymongo import MongoClient
# from bson import ObjectId
# import json

# # 连接到 MongoDB 数据库
# client = MongoClient('mongodb://localhost:27017/')  # 你的 MongoDB URI
# db = client['github']
# collection = db['github_commit_2022']  # 你的源集合
# target_collection = db['test_with_committer']  # 目标集合

# # 生成随机日期
# def random_date():
#     # 随机生成日期，假设日期范围在 2020-01-01 到 2023-01-01
#     start_date = datetime.datetime(2020, 1, 1)
#     end_date = datetime.datetime(2023, 1, 1)
#     delta = end_date - start_date
#     random_days = random.randint(0, delta.days)
#     random_date = start_date + datetime.timedelta(days=random_days)
#     return random_date

# # 生成随机 PersonInfo 数据
# def generate_random_person_info():
#     names = ["Alice", "Bob", "Charlie", "David", "Eve"]
#     emails = ["alice@example.com", "bob@example.com", "charlie@example.com", "david@example.com", "eve@example.com"]
    
#     return {
#         "name": random.choice(names),
#         "email": random.choice(emails),
#         "date": random_date()
#     }

# # 定义聚合管道，获取随机文档
# pipeline = [
#     {
#         "$match": {
#             "repository": "apache/skywalking"  # 替换为实际的 repository 值
#         }
#     },
#     {"$sample": {"size": 1}}  # size: 1 表示只返回一个文档
# ]

# # 获取随机文档
# random_document = collection.aggregate(pipeline)

# # 处理文档并插入到目标集合
# for doc in random_document:
#     # 生成随机的 committer 和 author
#     committer_info = generate_random_person_info()
#     author_info = generate_random_person_info()

#     # 为文档添加 committer 和 author 键
#     doc['committer'] = committer_info
#     doc['author'] = author_info

#     # 将更新后的文档插入到目标集合
#     target_collection.insert_one(doc)

#     # 输出插入的文档
#     print(json.dumps(doc, default=str))  # 使用 json.dumps 来打印出文档，日期字段会被转换为字符串

from pymongo import MongoClient
from bson import ObjectId
from pymongo import query

def filter_query(id=None, commit_sha=None, repository=None):
    query_conditions = []
    
    if id:
        query_conditions.append({"_id": ObjectId(id)})
    if commit_sha:
        query_conditions.append({"commit_sha": commit_sha})
    if repository:
        query_conditions.append({"repository": repository})
    
    # commit_sha 不为 null
    query_conditions.append({"commit_sha": {"$ne": None}})
    
    # datas 不为 null
    query_conditions.append({"datas": {"$ne": None}})
    
    # 返回符合所有条件的查询
    return {"$and": query_conditions}

# 示例用法：
# 假设有 MongoDB 连接
client = MongoClient('mongodb://localhost:27017/')
db = client['github']
collection = db['github_commit_2022']

# 构造查询条件
query_filter = filter_query(id="your_object_id", commit_sha="your_commit_sha", repository="your_repository")

# 执行查询
results = collection.find(query_filter)

# 打印查询结果
for result in results:
    print(result)
