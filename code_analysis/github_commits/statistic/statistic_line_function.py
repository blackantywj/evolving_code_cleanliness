from pymongo import MongoClient
import jieba 
from wordcloud import WordCloud

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['github']
collection = db['file_analyse_correct_20241228']

# 查询所有文档并提取所需信息
result_dict = {}

# 定义阈值
circle_threshold = 10  # 圈数的阈值
rows_threshold = 30  # 行数的阈值
chars_threshold = 80  # 字符数的阈值

# 初始化统计结果字典
change_summary = {
    "rows_norm_to_non_norm": 0,
    "rows_non_norm_to_norm": 0,
    "circle_norm_to_non_norm": 0,
    "circle_non_norm_to_norm": 0,
    "chars_norm_to_non_norm": 0,
    "chars_non_norm_to_norm": 0
}

def get_word_cloud(content):
    word_list = jieba.cut(content)
    word_space_split = ' '.join(word_list)
    wordcloud = WordCloud(background_color='white', width=1000, height=860, margin=2).generate(word_space_split)
    return wordcloud

# 检查函数：返回变化类型并统计变化
def check_norm_changes(old_value, new_value, threshold):
    if old_value <= threshold and new_value > threshold:
        return "规范 -> 不规范"
    elif old_value > threshold and new_value <= threshold:
        return "不规范 -> 规范"
    elif old_value <= threshold and new_value <= threshold:
        return "一直规范"
    elif old_value > threshold and new_value > threshold:
        return "一直不规范"
    else:
        return "未知状态"

for doc in collection.find():
    commit_sha = doc['commitSha']  # 键为 commitSha

    # 提取 methods 和 lines 数据
    methods_data = [
        {
            "newRows": method.get("newRows"),
            "oldRows": method.get("oldRows"),
            "newCircle": method.get("newCircle"),
            "oldCircle": method.get("oldCircle")
        }
        for method in doc.get('methods', [])
    ]

    lines_data = [
        {
            "newChars": line.get("newChars"),
            "oldChars": line.get("oldChars")
        }
        for line in doc.get('lines', [])
    ]

    # 保存数据到字典
    result_dict[commit_sha] = {
        "methods": methods_data,
        "lines": lines_data
    }

    # # 查询另一个表中的 commit 信息
    # commit_info = collection_commit_info.find_one({"commit_sha": commit_sha})

    # # 如果找到 commit 信息，提取并添加到结果字典中
    # commit_info_data = {
    #     # "author": commit_info.get("author"),
    #     # "date": commit_info.get("date"),
    #     "message": commit_info.get("message")
    # } if commit_info else {}

    # # 保存数据到字典
    # result_dict[commit_sha] = {
    #     "methods": methods_data,
    #     "lines": lines_data,
    #     "commit_info": commit_info_data
    # }

method_num = 0
method_line = 0
method_file = 0

for key, value in result_dict.items():
    for method in value['methods']:
        method_num += 1
    for line in value['lines']:
        method_line += 1
        
print(method_num)
print(method_line)
# for doc in collection.find():
#     commit_sha = doc['commitSha']
#     methods_data = []
    
#     # 遍历方法并检测规范性变化
#     for method in doc.get('methods', []):
#         method_check = {
#             "newRows": method.get("newRows"),
#             "oldRows": method.get("oldRows"),
#             "newCircle": method.get("newCircle"),
#             "oldCircle": method.get("oldCircle"),
#             "rows_change": check_norm_changes_and_update(
#                 method.get("oldRows"), method.get("newRows"),
#                 rows_threshold, "rows_norm_to_non_norm", "rows_non_norm_to_norm"
#             ),
#             "circle_change": check_norm_changes_and_update(
#                 method.get("oldCircle"), method.get("newCircle"),
#                 circle_threshold, "circle_norm_to_non_norm", "circle_non_norm_to_norm"
#             )
#         }
#         methods_data.append(method_check)

#     lines_data = []

#     # 遍历代码行并检测规范性变化
#     for line in doc.get('lines', []):
#         line_check = {
#             "newChars": line.get("newChars"),
#             "oldChars": line.get("oldChars"),
#             "chars_change": check_norm_changes_and_update(
#                 line.get("oldChars"), line.get("newChars"),
#                 chars_threshold, "chars_norm_to_non_norm", "chars_non_norm_to_norm"
#             )
#         }
#         lines_data.append(line_check)

#     # 保存结果
#     result_dict[commit_sha] = {
#         "methods": methods_data,
#         "lines": lines_data
#     }