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

plt.rcParams['font.family'] = 'Times New Roman'

# 用于处理每一条提交信息的函数
def parse_commit_line(line, condition, my_need_repo):
    commit_info = {}
    
    # 提取提交ID
    commit_id_match = re.search(r"提交: (\S+)", line)
    if commit_id_match:
        commit_info["commit_id"] = commit_id_match.group(1)
        repo_commit_id_match = re.match(r"https://github.com/([^/]+)/([^/]+)/commit/.*", commit_info["commit_id"])

        if repo_commit_id_match:
            repo_name = f"{repo_commit_id_match.group(1)}/{repo_commit_id_match.group(2)}"
            if repo_name != my_need_repo:
                return {}
    
    # 提取提交人
    author_match = re.search(r"提交人: (\S+)", line)
    if author_match:
        commit_info["author"] = author_match.group(1)
        # if commit_info["author"] == 'web-flow':
        #     return {}
    
    # 提取提交时间
    date_match = re.search(r"提交时间: (\S+)", line)
    if date_match:
        commit_info["date"] = date_match.group(1)
    
    # 提取涉及的文件
    file_match = re.search(r"文件: (\S+)", line)
    if file_match:
        commit_info["file"] = file_match.group(1)
    
    # 提取函数
    if '函数' in condition:
        function_match = re.search(r"函数: (.+?)(?=\n|$)", line)
        if function_match:
            commit_info["function"] = function_match.group(1).strip()
    
    # 提取函数复杂度变化
    complexity_match = re.search(r"%s: (.+)" % condition, line)
    if complexity_match:
        commit_info["complexity_change"] = complexity_match.group(1)
    
    return commit_info

# 从txt文件中读取数据并整理成字典列表
def parse_commits_from_file(file_path, condition, my_need_repo):
    commit_list = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # 临时变量用于存储单个提交的信息
        current_commit = ""
        
        for line in lines:
            # 如果当前行是提交开始的标志（例如"提交:"），则开始处理一个新的提交
            if line.startswith("提交: "):
                # 如果已经存在一个提交，则处理并添加到列表
                if current_commit:
                    commit_info = parse_commit_line(current_commit, condition, my_need_repo)
                    # 如果提交信息包含关键字段（例如提交ID、提交人、提交时间等），则加入列表
                    if "commit_id" in commit_info and "author" in commit_info:
                        commit_list.append(commit_info)
                
                # 开始新的提交
                current_commit = line.strip()
            else:
                # 其他行合并到当前提交信息中
                if line.strip():  # 忽略空行
                    current_commit += " " + line.strip()
        
        # 添加最后一个提交的信息
        if current_commit:
            commit_info = parse_commit_line(current_commit, condition, my_need_repo)
            if "commit_id" in commit_info and "author" in commit_info and "date" in commit_info:
                commit_list.append(commit_info)
    
    return commit_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="argparse 处理命令行参数")
    
    parser.add_argument("-e", "--element", type=str, default="ClassNames")
    parser.add_argument("-c", "--condition", type=str, default="类名变化")
    parser.add_argument("-mnr", "--my_need_repo", type=list, nargs='*', default=[
    # "apache/dubbo",
    # "apache/kafka",
    # "apache/incubator-seata",
    # "apache/flink",
    # "apache/skywalking",
    # "apache/rocketmq",
    # "apache/shardingsphere",
    # "apache/hadoop",
    # "apache/pulsar",
    # "apache/druid",
    # "apache/zookeeper"
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
    "spring-projects/spring-boot",
    "spring-projects/spring-framework",
    "spring-projects/spring-security",
    "spring-projects/spring-authorization-server",
    "spring-projects/spring-ai",
    "spring-projects/spring-data-jpa",
    "spring-projects/spring-kafka",
    "spring-projects/spring-batch",
    "spring-projects/spring-session",
    "spring-projects/spring-data-mongodb"
    ])

    parser.add_argument("-r", "--rank", type=int, default=5)
    parser.add_argument("-t", "--threshold", type=int, default=80)
    
    args = parser.parse_args()

    # 输出解析结果
    file_path = '/home/cumt/workspace/code_analysis/JavaPatchParser/circle/data_google_spring_4+/%s/detail.txt' % args.element  # 你可以将此文件路径替换为实际文件路径
    # 按月份统计
    monthly_stats_k_p = defaultdict(int)
    monthly_stats_k_n = defaultdict(int)
    monthly_stats_p = defaultdict(int)
    monthly_stats_n = defaultdict(int)
    monthly_stats = defaultdict(int)
    for mnr in args.my_need_repo:
        commits = parse_commits_from_file(file_path, args.condition, mnr)

        # 按提交时间排序数据（从早到晚）
        data_sorted = sorted(commits, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))

        # 统计每个提交人按时间的提交次数
        commit_counts_k_p = defaultdict(lambda: defaultdict(int))
        commit_counts_k_n = defaultdict(lambda: defaultdict(int))
        commit_counts_p = defaultdict(lambda: defaultdict(int))
        commit_counts_n = defaultdict(lambda: defaultdict(int))
        # 遍历数据，统计符合条件的提交
        for entry in data_sorted:
            # 获取复杂度变化字符串
            complexity_change = entry['complexity_change']
            # 提取变化前后的复杂度
            match = re.match(r"(\S+) -> (\S+)", complexity_change)
            
            if match:
                before = str(match.group(1))  # 提取前面的数字
                after = str(match.group(2))   # 提取后面的数字
            # before, after = complexity_change.split(' -> ')
            # before = int(before)
            # after = int(after)
            
            # 判断变化后是否超过threshold
            if after == 'true' and before == 'true':
                commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                commit_counts_k_p[entry['author']][commit_time] += 1
            elif after == 'false' and before == 'true':
                commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                commit_counts_p[entry['author']][commit_time] += 1            
            elif after == 'true' and before == 'false':
                commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                commit_counts_n[entry['author']][commit_time] += 1   
            elif after == 'false' and before == 'false':
                commit_time = datetime.strptime(entry['date'], "%Y-%m-%d").date()
                commit_counts_k_n[entry['author']][commit_time] += 1   

        for k, v in commit_counts_k_p.items():     
            for d, count in commit_counts_k_p[k].items():
                month = f"{d.year}-{d.month:02}"  # 获取年份-月份
                monthly_stats[month] += count
                    
        for k, v in commit_counts_k_p.items():     
            for d, count in commit_counts_k_p[k].items():
                month = f"{d.year}-{d.month:02}"  # 获取年份-月份
                monthly_stats_k_p[month] += count

        for k, v in commit_counts_k_n.items():     
            for d, count in commit_counts_k_n[k].items():
                month = f"{d.year}-{d.month:02}"  # 获取年份-月份
                monthly_stats_k_n[month] += count

        for k, v in commit_counts_p.items():     
            for d, count in commit_counts_p[k].items():
                month = f"{d.year}-{d.month:02}"  # 获取年份-月份
                monthly_stats_p[month] += count
    
        for k, v in commit_counts_n.items():     
            for d, count in commit_counts_n[k].items():
                month = f"{d.year}-{d.month:02}"  # 获取年份-月份
                monthly_stats_n[month] += count
     
    # 保存数据到文件
    # for i, group in enumerate(data_groups):
    # 统一时间轴
    all_months = sorted(set(monthly_stats.keys()).union(monthly_stats_k_n.keys()))
    values1 = {month: monthly_stats_k_p.get(month, 0) for month in all_months}
    values2 = {month: monthly_stats_p.get(month, 0) for month in all_months}
    values3 = {month: monthly_stats_n.get(month, 0) for month in all_months}
    values4 = {month: monthly_stats_k_n.get(month, 0) for month in all_months}
    # 保存到文件
    with open(f'{args.element}_{args.my_need_repo[0].split("/")[0]}.json', 'w') as f:
        json.dump({'months': all_months, 'values1': values1, 'values2': values2, 'values3':values3, 'values4':values4}, f)