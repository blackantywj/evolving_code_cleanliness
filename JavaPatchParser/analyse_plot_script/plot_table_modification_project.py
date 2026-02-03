# if __name__ == '__main__':
#     with open("circle/data/MethodCircles/detail.txt", 'r') as f:
#         content = f.read()
#     print(content)

import re
import json
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
import argparse

from pymongo import MongoClient
from datetime import datetime

# 连接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")  # 替换为你的 MongoDB URI
db = client["github"]  # 替换为你的数据库名称
collection = db["github_commit"]  # 替换为你的集合名称

if __name__ == "__main__":
    VALID_CONFIGS = {
    # "MethodCircles": {"condition": "函数复杂度变化", "threshold": 10},
    # "MethodRows": {"condition": "函数行数变化", "threshold": 30},
    # "FileRows": {"condition": "文件行数变化", "threshold": 2000},
    # "LineChars": {"condition": "行字符数变化", "threshold": 80},
    "TryCatchNum":{"condition": "Try-Catch个数变化"},
    "MethodNames":{"condition": "函数变量名变化"},
    "ClassNames":{"condition": "类名变化"},
    "VariableNames":{"condition": "函数参数名变化"},
    }
    parser = argparse.ArgumentParser(description="argparse 处理命令行参数")
    parser.add_argument("-mnr", "--my_need_repo", type=list, default=[
    "apache/dubbo",
    "apache/kafka",
    "apache/flink",
    "apache/skywalking",
    "apache/rocketmq",
    "apache/shardingsphere",
    "apache/hadoop",
    "apache/pulsar",
    "apache/druid",
    "apache/zookeeper"
    # "google/guava",
    # "google/gson", 
    # "google/ExoPlayer", 
    # "google/dagger", 
    # "google/guice", 
    # "google/auto", 
    # "google/tsunami-security-scanner",
    # "google/error-prone", 
    # "google/closure-compiler", 
    # "google/nomulus"
    # "spring-projects/spring-boot",
    # "spring-projects/spring-framework",
    # "spring-projects/spring-security",
    # "spring-projects/spring-authorization-server",
    # "spring-projects/spring-ai",
    # "spring-projects/spring-data-jpa",
    # "spring-projects/spring-kafka",
    # "spring-projects/spring-batch",
    # "spring-projects/spring-session",
    # "spring-projects/spring-data-mongodb"
    ])
    parser.add_argument("-com", "--company", type=str, default="apache")
    parser.add_argument("-r", "--rank", type=int, default=1)
    argu_need_plot_commit_p = defaultdict(lambda: defaultdict(int))
    argu_need_plot_commit_n = defaultdict(lambda: defaultdict(int))
    args = parser.parse_args()
    start_time = "2022-01-01"  # 起始时间
    end_time = "2024-12-15"  # 截止时间
    # 查询条件
    for repository_name in args.my_need_repo:
        query = {
            "repository": repository_name,
            "release_time": {"$gte": start_time, "$lte": end_time}  # 时间区间
        }

        # 执行查询
        results = collection.find(query)

        # 输出结果
        for document in results:
            print(document)
            oldtcn = document["old"]
            newtcn = document["new"]

        # 关闭连接（可选）
        client.close()

    for key, value in VALID_CONFIGS.items():
        element = key
        condition = VALID_CONFIGS[element]['condition']
        if key in ["LineChars", "MethodCircles", "MethodRows", "FileRows"]:
            threshold = VALID_CONFIGS[element]['threshold']
        # parser.add_argument("-e", "--element", type=str, default=key)
        # args = parser.parse_args()
        # parser.add_argument("-c", "--condition", type=str, default=VALID_CONFIGS[args.element]['condition'])
        # parser.add_argument("-t", "--threshold", type=int, default=VALID_CONFIGS[args.element]['threshold'])
        # args = parser.parse_args()
    
        need_plot_commit_p = defaultdict(lambda: defaultdict(dict))
        need_plot_commit_n = defaultdict(lambda: defaultdict(dict))
        need_plot_commit = defaultdict(lambda: defaultdict(dict))
        
        for mnr in args.my_need_repo:
            # 输出解析结果
            file_path = 'circle/data_apache_with_true_committer/%s/detail.txt' % element  # 你可以将此文件路径替换为实际文件路径
            commits = parse_commits_from_file(file_path, condition, mnr)

            # 按提交时间排序数据（从早到晚）
            data_sorted = sorted(commits, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))

            # 统计每个提交人按时间的提交次数
            commit_counts_p = defaultdict(lambda: defaultdict(int))
            commit_counts_n = defaultdict(lambda: defaultdict(int))
            commit_counts = defaultdict(lambda: defaultdict(int))
            
            # 遍历数据，统计符合条件的提交
            for entry in data_sorted:
                # if entry['author'] == 'null':
                #     continue
                # 获取复杂度变化字符串
                complexity_change = entry['complexity_change']
                
                # 提取变化前后的复杂度
                # before, after = complexity_change.split(' -> ')
                # before = int(before)
                # after = int(after)
                
                if key in ["LineChars", "MethodCircles", "MethodRows", "FileRows"]:
                    match = re.match(r"(\d+) -> (\d+)", complexity_change)
                
                    if match:
                        before = int(match.group(1))  # 提取前面的数字
                        after = int(match.group(2))   # 提取后面的数字
                    if before != after:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts[entry['author']][commit_time] += 1
                    
                    # 判断变化后的复杂度是否超过 10
                    if before < threshold and after > threshold:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_n[entry['author']][commit_time] += 1

                    elif before > threshold and after < threshold:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_p[entry['author']][commit_time] += 1
                        
                elif key == 'TryCatchNum':
                    match = re.match(r"(\d+) -> (\d+)", complexity_change)
                
                    if match:
                        before = int(match.group(1))  # 提取前面的数字
                        after = int(match.group(2))   # 提取后面的数字
                        
                    if before != after:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts[entry['author']][commit_time] += 1
                    
                    # 判断变化后的复杂度是否超过 10
                    if before > after:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_n[entry['author']][commit_time] += 1

                    elif before < after:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_p[entry['author']][commit_time] += 1      
                                      
                elif key in ["MethodNames", "ClassNames", "VariableNames"]:
                    match = re.match(r"(\S+) -> (\S+)", complexity_change)
                
                    if match:
                        before = str(match.group(1))  # 提取前面的数字
                        after = str(match.group(2))   # 提取后面的数字     
                                       
                    if before != after:
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts[entry['author']][commit_time] += 1
                    
                    # 判断变化后的复杂度是否超过 10
                    if before == "true" and after == "false":
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_n[entry['author']][commit_time] += 1

                    elif before == "false" and after == "true":
                        commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                        commit_counts_p[entry['author']][commit_time] += 1    
                                        
            author_with_commit_n_num = defaultdict(lambda: defaultdict(int))
            author_with_commit_p_num = defaultdict(lambda: defaultdict(int))
            author_with_commit_num = defaultdict(lambda: defaultdict(int))
            
            for person, commits in commit_counts_p.items():
                total = 0
                for date, time in commits.items():
                    total += time
                author_with_commit_p_num[person] = total

            for person, commits in commit_counts_n.items():
                total = 0
                for date, time in commits.items():
                    total += time
                author_with_commit_n_num[person] = total

            for person, commits in commit_counts.items():
                total = 0
                for date, time in commits.items():
                    total += time
                author_with_commit_num[person] = total
        
            author_with_commit_name = sorted(author_with_commit_num.items(), key=lambda x: x[1], reverse=True)[:args.rank]     
            author_with_commit_p_name = sorted(author_with_commit_p_num.items(), key=lambda x: x[1], reverse=True)
            author_with_commit_n_name = sorted(author_with_commit_n_num.items(), key=lambda x: x[1], reverse=True)
            # need_plot_commit[mnr.split('/')[1]] = author_with_commit_name
            
            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts_p.items():
                if person == author_with_commit_p_name[0][0]:
                    need_plot_commit_p[mnr.split('/')[1]][person] = author_with_commit_p_num[person]

            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts_n.items():
                if person == author_with_commit_n_name[0][0]:
                    need_plot_commit_n[mnr.split('/')[1]][person] = author_with_commit_n_num[person]

            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts.items():
                if person == author_with_commit_name[0][0]:
                    need_plot_commit[mnr.split('/')[1]][person] = author_with_commit_name[0][1]
        
        need_plot_commit_p = {k: dict(sorted(v.items(), key=lambda x: x[1])) for k, v in need_plot_commit_p.items()}
        need_plot_commit_n = {k: dict(sorted(v.items(), key=lambda x: x[1])) for k, v in need_plot_commit_n.items()}
        # need_plot_commit_p = sorted(need_plot_commit_p.values().items(), key=lambda x: x[1], reverse=True)
        # need_plot_commit_n = sorted(need_plot_commit_n.values().items(), key=lambda x: x[1], reverse=True)
        argu_need_plot_commit_p[key] = need_plot_commit_p
        argu_need_plot_commit_n[key] = need_plot_commit_n
        
    for project in [
        "dubbo",
        "kafka",
        "flink",
        "skywalking",
        "rocketmq",
        "shardingsphere",
        "hadoop",
        "pulsar",
        "druid",
        "zookeeper"
        # "guava",
        # "gson",
        # "ExoPlayer",
        # "dagger",
        # "guice",
        # "auto",
        # "tsunami-security-scanner",
        # "error-prone",
        # "closure-compiler",
        # "nomulus"
        # "spring-boot",
        # "spring-framework",
        # "spring-security",
        # "spring-authorization-server",
        # "spring-ai",
        # "spring-data-jpa",
        # "spring-kafka",
        # "spring-batch",
        # "spring-session",
        # "spring-data-mongodb"
    ]:  
        print(project, end = '')
        for argu in ["TryCatchNum", "ClassNames", "MethodNames", "VariableNames"]:
        # for argu in ["MethodCircles", "MethodRows", "FileRows"]:
            if project in argu_need_plot_commit_p[argu]:
                print('&', list(argu_need_plot_commit_p[argu][project].keys())[0], '&', list(argu_need_plot_commit_p[argu][project].values())[0], end = '')
            else:
                print('&', '-', '&', '0', end = '')
            if project in argu_need_plot_commit_n[argu]:
                print('&', list(argu_need_plot_commit_n[argu][project].keys())[0], '&', list(argu_need_plot_commit_n[argu][project].values())[0], end = '')
            else:
                print('&', '-','&', '0', end = '')            
            # print('&', list(argu_need_plot_commit_p[argu][project].keys())[0], '&', list(argu_need_plot_commit_p[argu][project].values())[0], \
            #     '&', list(argu_need_plot_commit_n[argu][project].keys())[0], '&', list(argu_need_plot_commit_n[argu][project].values())[0])
        print("\\\\")