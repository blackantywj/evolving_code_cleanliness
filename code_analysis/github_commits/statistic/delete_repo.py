from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['github']  # 替换为你的数据库名称

# 遍历所有集合并删除 `repository: "b"` 的文档
for collection_name in db.list_collection_names():
    collection = db[collection_name]
    result = collection.delete_many({"repository": "b"})
    print(f"Collection {collection_name}: Deleted {result.deleted_count} documents.")

print("All matching documents have been deleted.")
