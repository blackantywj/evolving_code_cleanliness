from pymongo import MongoClient

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['google']
collection = db['github_commit']

# # 指定查询条件
# repository_value = "apache/skywalking"  # 你要匹配的 repository 字符串

# # 聚合查询
# pipeline = [
#     {
#         "$match": {
#             "repository": repository_value  # 匹配 repository
#         }
#     },
#     {
#     "$match": {
#         "datas.data": {"$ne": None},  # 排除 data 为 None 的文档
#     }
#     },
#     {
#         "$unwind": "$datas"  # 将 datas 数组展平，每个元素会成为独立的文档
#     },
#     {
#         "$group": {
#             "_id": None,  # 不分组，统计所有符合条件的文档
#             "total_elements": {"$sum": 1}  # 计算展平后的元素总数
#         }
#     }
# ]

# # 执行聚合查询
# result = list(collection.aggregate(pipeline))

# # 输出结果
# if result:
#     print(f"符合条件的 `datas` 数组中元素的总量: {result[0]['total_elements']}")
# else:
#     print("没有符合条件的文档")

# pipeline = [
#     {
#     "$match": {
#         "repository": repository_value  # 匹配 repository
#     }
#     },
#     {"$sample": {"size": 10}}  # size: 1 表示只返回一个文档
# ]

# random_document = collection.aggregate(pipeline)

# # 输出随机文档
# for doc in random_document:
#     print(doc)

# 设置查询条件（例如：查询所有age为30的文档）
# query = {"repository": "apache/skywalking"}

# # 获取满足查询条件的文档数量
# count = collection.count_documents(query)

# print(f"符合条件的数据数量: {count}")

'''
- apache/dubbo: 多版本名
- apache/kafka: 多版本
- apache/incubator-seata: 多版本
- apache/flink: 有主分支
- apache/skywalking: 多版本，有主分支 github_commit
- apache/rocketmq: 多版本，main、master、feature都有
- apache/shardingsphere: 只有主分支 ?
- apache/hadoop: 多版本 ?
- apache/pulsar: 多版本，主分支 ?
- apache/druid: 多版本 ?
- apache/zookeeper: 多版本，主分支 github_commit
'''
'''
"google/guava" 
"google/gson" 
"google/ExoPlayer*" 
"google/dagger" 
"google/guice*" 
"google/auto" 
"google/tsunami-security-scanner" 
"google/closure-compiler" 
"google/error-prone" 
"google/nomulus"
'''

# spring-projects/spring-boot" 
# "spring-projects/spring-framework" 
# "spring-projects/spring-security" 
# "spring-projects/spring-authorization-server" 
# "spring-projects/spring-ai" 
# "spring-projects/spring-data-jpa" 
# "spring-projects/spring-kafka" 
# "spring-projects/spring-batch" 
# "spring-projects/spring-session" 
# "spring-projects/spring-data-mongodb

repository = "google/nomulus"

commits = collection.find({"repository": repository, "download": {"$exists": True}})

dataTotal = set()
commitNum = 0
dataNum = 0
start_time = "2022-01-01"
end_time = "2024-12-15"
for commit in commits:
    commitNum += 1
    datas = commit['datas']
    release_time = commit["release_time"]
    if commit['commit_sha'] == None:
        continue
    if start_time:
        if release_time <= start_time:
            continue
    if end_time:
        if release_time >= end_time:
            continue
    if datas == None:
        continue
    for data in datas:
        # if data == None:
        #     print(1)
        if data != None:
            dataTotal.add(data['fileName'])
        # print(data)
        # if data['newFileContent'] != "404" and data['oldFileContent'] != "404":
            # dataTotal.add(data)
            dataNum += 1
print(commitNum, dataNum)
    # fileNamelist = [i['fileName'] for i in datas if i != None]
    # print(len(set(fileNamelist)) == len(fileNamelist))
    # print(commit)


# db.github_commit_2022.aggregate([
#   {
#     $match: { repository: "apache/dubbo" } // 查找repository为"apache/dubbo"的文档
#   },
#   {
#     $project: {
#       datasCount: {
#         $size: {
#           $filter: {
#             input: "$datas", // 要过滤的数组
#             as: "item", // 数组中的每个元素的别名
#             cond: { $and: [
#               { $ne: ["$$item", {}] }, // 过滤掉空字典
#               { $ne: ["$$item", null] } // 过滤掉null值
#             ]}
#           }
#         }
#       }
#     }
#   }
# ])

# db.github_commit_2022.aggregate([
#   {
#     $match: { repository: "apache/dubbo" } // 查找repository为"apache/dubbo"的文档
#   },
#   {
#     $project: {
#       datasCount: {
#         $size: {
#           $filter: {
#             input: { 
#               $ifNull: ["$datas", []] // 如果datas为null，则将其转换为一个空数组
#             },
#             as: "item",
#             cond: { $and: [
#               { $ne: ["$$item", {}] }, // 过滤掉空字典
#               { $ne: ["$$item", null] } // 过滤掉null值
#             ]}
#           }
#         }
#       }
#     }
#   }
# ])