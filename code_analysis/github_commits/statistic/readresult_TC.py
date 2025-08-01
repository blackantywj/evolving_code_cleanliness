import json 

# 检查函数：返回变化类型并统计变化
def check_norm_changes(old_value, new_value):
    if old_value > new_value:
        return "规范 -> 不规范"
    elif old_value < new_value:
        return "不规范 -> 规范"
    elif old_value == new_value:
        return "一直规范"
    else:
        return "未知状态"

with open("result_trynum.json") as file:
    result_dict = json.load(file)

# 初始化分类字典
classified_commits = {
    "rows_positive": {},  # Rows: 正面修改大于负面修改
    "rows_negative": {},  # Rows: 负面修改大于正面修改
    # "circle_positive": {},  # Circle: 正面修改大于负面修改
    # "circle_negative": {},  # Circle: 负面修改大于正面修改
    # "chars_positive": {},  # Chars: 正面修改大于负面修改
    # "chars_negative": {},  # Chars: 负面修改大于正面修改
}

# max_rows_positive = {}
# max_rows_negative = {}
# max_circle_positive = {}
# max_circle_negative = {}
# max_chars_positive = {}
# max_chars_negative = {}

for commit_sha, value in result_dict.items():
    # Rows
    summary = value["commit_summary"]
        
    if summary["rows_non_norm_to_norm"] > summary["rows_norm_to_non_norm"]:
        classified_commits["rows_positive"][commit_sha] = "{%d}_{%d}" % (summary["rows_non_norm_to_norm"], summary["rows_norm_to_non_norm"])
        
    elif summary["rows_norm_to_non_norm"] > summary["rows_non_norm_to_norm"]:
        classified_commits["rows_negative"][commit_sha] = "{%d}_{%d}" % (summary["rows_norm_to_non_norm"], summary["rows_non_norm_to_norm"])

    # # Circle
    # if summary["circle_non_norm_to_norm"] > summary["circle_norm_to_non_norm"]:
    #     classified_commits["circle_positive"][commit_sha] = "{%d}_{%d}" % (summary["circle_non_norm_to_norm"], summary["circle_norm_to_non_norm"])
    # elif summary["circle_norm_to_non_norm"] > summary["circle_non_norm_to_norm"]:
    #     classified_commits["circle_negative"][commit_sha] ="{%d}_{%d}" % (summary["circle_norm_to_non_norm"], summary["circle_non_norm_to_norm"])

    # # Chars
    # if summary["chars_non_norm_to_norm"] > summary["chars_norm_to_non_norm"]:
    #     classified_commits["chars_positive"][commit_sha] = "{%d}_{%d}" % (summary["chars_non_norm_to_norm"], summary["chars_norm_to_non_norm"])
    # elif summary["chars_norm_to_non_norm"] > summary["chars_non_norm_to_norm"]:
    #     classified_commits["chars_negative"][commit_sha] = "{%d}_{%d}" % (summary["chars_norm_to_non_norm"], summary["chars_non_norm_to_norm"])

print(classified_commits)
# print(data)
