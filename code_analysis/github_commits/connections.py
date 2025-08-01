import pymongo
from urllib.parse import quote_plus

MONGO_URL = "mongodb://127.0.0.1:27017/"
# MONGO_URL = "mongodb://root:Yan%40123456@dds-bp1e9c847ff7f3c4-pub.mongodb.rds.aliyuncs.com:3717"
# MONGO_URL = "mongodb://root:Yan@123456@dds-bp1e9c847ff7f3c4-pub.mongodb.rds.aliyuncs.com:3717/admin"
# MONGO_URL = quote_plus(MONGO_URL)
# print(MONGO_URL)

# 
def get_client():
    client = pymongo.MongoClient(MONGO_URL)
    return client


def get_collection(collection):
    client = get_client()
    database = client["github"]
    return database[collection]


def init_index():
    collection = get_collection("github_commit")
    collection.create_index()


res = get_client()
print(res)
# get_collection("github")