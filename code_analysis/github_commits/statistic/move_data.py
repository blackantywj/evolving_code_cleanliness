from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")  # 替换为你的 MongoDB 地址
source_db = client["github_2022"]  # 源数据库
target_db = client["github"]  # 目标数据库

source_collection = source_db["github_commit_2022"]  # 源集合
target_collection = target_db["github_commit_2022"]  # 目标集合

# 筛选条件：repository 为 apache/dubbo 或 apache/kafka
query = {"repository": {"$in": ["apache/dubbo", "apache/kafka"]}}

# 查找符合条件的文档
documents_to_move = list(source_collection.find(query))

# 如果有文档需要移动
if documents_to_move:
    # 插入文档到目标集合
    target_collection.insert_many(documents_to_move)

    # 从源集合中删除这些文档
    source_collection.delete_many(query)

    print(f"Moved {len(documents_to_move)} documents to the target collection.")
else:
    print("No documents matched the query.")
