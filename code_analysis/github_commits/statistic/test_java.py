from pymongo import MongoClient
from pymongo.collection import Collection
from bson.son import SON

def query_full_count(collection: Collection, filter_condition: dict) -> int:
    # 构建聚合管道
    pipeline = [
        {"$match": {
            **filter_condition,
            "datas": {"$exists": True, "$type": "array"}  # 确保 datas 存在且为数组
        }},
        {"$project": {
            "files": {"$size": "$datas"},
            "repository": "apache/skywalking"
        }},
        {"$group": {
            "_id": "$repository",
            "files": {"$sum": "$files"}
        }}
    ]

    
    # 执行聚合查询
    aggregate_result = collection.aggregate(pipeline)
    
    # 提取并求和
    total_files = sum(doc["files"] for doc in aggregate_result)
    return total_files

# 使用示例
client = MongoClient("mongodb://localhost:27017/")
db = client["github"]
collection = db["github_commit_2022"]

# 假设 filter_condition 是一个合法的 MongoDB 查询条件
filter_condition = {"repository": "apache/skywalking"}
result = query_full_count(collection, filter_condition)
print("Total files:", result)