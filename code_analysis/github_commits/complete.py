from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库
db = client['github']

# 获取数据库中的所有集合名称
collections = db.list_collection_names()

# 遍历每个集合
for collection_name in collections:
    collection = db[collection_name]
    # 查询缺少 'download' 字段的文档数量
    missing_count = collection.count_documents({'download': {'$exists': False}})
    if missing_count > 0:
        print(f"集合 '{collection_name}' 中有 {missing_count} 个文档缺少 'download' 字段。")
    else:
        print(f"集合 '{collection_name}' 中所有文档都包含 'download' 字段。")
