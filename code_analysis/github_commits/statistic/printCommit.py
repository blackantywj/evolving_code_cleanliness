from pymongo import MongoClient
import jieba 
from wordcloud import WordCloud
import json

project = 'spring'

# 连接到 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['github']
collection = db['file_analyse_correct_20241228']

# 原始集合
collection_commits = db['github']

# 包含其他信息的集合
collection_commit_info = db['github_commit']

# 查询所有文档并提取所需信息
result_dict = {}

# 定义阈值
circle_threshold = 10  # 圈数的阈值
rows_threshold = 30  # 行数的阈值
chars_threshold = 80  # 字符数的阈值
filerows_threshold = 2000

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
    commit_sha = doc['commitSha']
    # if "com/google" in doc['commitUrl']:
    #     continue
    commit_summary = {
        "rows_norm_to_non_norm": 0,
        "rows_non_norm_to_norm": 0,
        "rows_norm":0,
        "rows_non_norm":0,
        "circle_norm_to_non_norm": 0,
        "circle_non_norm_to_norm": 0,
        "circle_norm":0,
        "circle_non_norm":0,
        "chars_norm_to_non_norm": 0,
        "chars_non_norm_to_norm": 0,
        "chars_norm":0,
        "chars_non_norm":0,
        "filerows_norm_to_non_norm": 0,
        "filerows_non_norm_to_norm": 0,
        "filerows_norm":0,
        "filerows_non_norm":0,
    }
    
    # 遍历方法并统计变化
    for method in doc.get('methods', []):
        rows_change = check_norm_changes(
            method.get("oldRows"), method.get("newRows"), rows_threshold
        )
        circle_change = check_norm_changes(
            method.get("oldCircle"), method.get("newCircle"), circle_threshold
        )
        
        if rows_change == "规范 -> 不规范":
            commit_summary["rows_norm_to_non_norm"] += 1
        elif rows_change == "不规范 -> 规范":
            commit_summary["rows_non_norm_to_norm"] += 1
        elif rows_change == "一直规范":
            commit_summary["rows_norm"] += 1
        elif rows_change == "一直不规范":
            commit_summary["rows_non_norm"] += 1

        if circle_change == "规范 -> 不规范":
            commit_summary["circle_norm_to_non_norm"] += 1
        elif circle_change == "不规范 -> 规范":
            commit_summary["circle_non_norm_to_norm"] += 1
        elif circle_change == "一直规范":
            commit_summary["circle_norm"] += 1
        elif circle_change == "一直不规范":
            commit_summary["circle_non_norm"] += 1
                
    # 遍历代码行并统计变化
    for line in doc.get('lines', []):
        chars_change = check_norm_changes(
            line.get("oldChars"), line.get("newChars"), chars_threshold
        )
        
        if chars_change == "规范 -> 不规范":
            commit_summary["chars_norm_to_non_norm"] += 1
        elif chars_change == "不规范 -> 规范":
            commit_summary["chars_non_norm_to_norm"] += 1
        elif chars_change == "一直规范":
            commit_summary["chars_norm"] += 1
        elif chars_change == "一直不规范":
            commit_summary["chars_non_norm"] += 1
            
    # 遍历文件代码行并统计变化
    filerows_change = check_norm_changes(
        doc.get("oldRows", 0), line.get("newRows", 0), filerows_threshold
    )
    if filerows_change == "规范 -> 不规范":
        commit_summary["filerows_norm_to_non_norm"] += 1
    elif filerows_change == "不规范 -> 规范":
        commit_summary["filerows_non_norm_to_norm"] += 1
    elif filerows_change == "一直规范":
        commit_summary["filerows_norm"] += 1
    elif filerows_change == "一直不规范":
        commit_summary["filerows_non_norm"] += 1

    # commit_info = collection_commit_info.find_one({"commit_sha": commit_sha})

    # # 如果找到 commit 信息，提取并添加到结果字典中
    # commit_info_data = {
    #     # "author": commit_info.get("author"),
    #     # "date": commit_info.get("date"),
    #     "message": commit_info.get("message")
    # } if commit_info else {}

    # 保存每个 commit 的统计结果
    result_dict[commit_sha] = {"commit_summary": commit_summary}

print(result_dict["559f12154a40f3bf6944c84e808f488e9f36242d"])
print(result_dict["375f33a390892c384a0fdbe9a65aa8e4a5094f9b"])
print(result_dict["c7f1872bd1ba45cbe40d4c7c171a683e9928f851"])