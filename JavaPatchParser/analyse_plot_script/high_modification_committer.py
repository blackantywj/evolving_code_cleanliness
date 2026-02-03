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
        if commit_info["author"] == 'web-flow':
            return {}
    
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
            if line.startswith("提交:"):
                # 如果已经存在一个提交，则处理并添加到列表
                if current_commit:
                    commit_info = parse_commit_line(current_commit, condition, my_need_repo)
                    # 如果提交信息包含关键字段（例如提交ID、提交人、提交时间等），则加入列表
                    if "commit_id" in commit_info and "author" in commit_info and "date" in commit_info:
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
    VALID_CONFIGS = {
    # "MethodCircles": {"condition": "函数复杂度变化", "threshold": 10},
    # "MethodRows": {"condition": "函数行数变化", "threshold": 30},
    # "FileRows": {"condition": "文件行数变化", "threshold": 2000},
    "LineChars": {"condition": "行字符数变化", "threshold": 80},
    "TryCatchNum":{"condition": "Try-Catch个数变化"},
    "MethodNames":{"condition": "函数变量名变化"},
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
    parser.add_argument("-r", "--rank", type=int, default=1)
    argu_need_plot_commit_p = defaultdict(lambda: defaultdict(int))
    argu_need_plot_commit_n = defaultdict(lambda: defaultdict(int))
    args = parser.parse_args()
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
                if entry['author'] == 'null':
                    continue
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
                                      
                elif key == 'MethodNames':
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
        for argu in ["LineChars", "TryCatchNum", "MethodNames"]:
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
            # for (pKey, pValue), (_, nValue) in zip(argu_need_plot_commit_p, argu_need_plot_commit_n):
            #     if project not in pValue:
            #         pValue[project] = {'-', 0}
            #     if project in nValue:
            #         nValue[project] = {'-', 0}
                
            # print(pKey, "\n")
            #   Druid & GitHub & 7     & GitHub & 13    & GitHub & 72    
            #    & GitHub & 103   & GitHub & 0     & GitHub & 6
            
        
    
    # print("test")
    
    # for project, contributors in need_plot_commit.items():
    #     # 确保贡献者列表有 4 个，不足的用 ('-', 0) 补充
    #     contributors += [('-', 0)] * (4 - len(contributors))
        
    #     # 打印项目名
    #     print(f"& {project:20}", end=" ")
    #     # 打印每个贡献者的用户名和贡献数
    #     for name, count in contributors:
    #         print(f"& {name:15} & {count:<5}", end=" ")
    #     print("\\\\")  # 每行末尾换行符号
    
    # 准备绘图数据
    # fig, ax = plt.subplots(figsize=(10, 6))    
    # for person, commits in need_plot_commit.items():      
    #     dates = sorted(commits.keys())
    #     counts = [commits[date] for date in dates]
    #     ax.plot(dates, counts, label=person, marker='o')
        # ax.set_legend("{} {}".format(person, author_with_commit_num[person]))
    
    # Set the title, labels, and other properties of the plot
    # ax.set_title(f'Number of Commits Increasing {args.element} Over Time')
    # ax.set_xlabel('Date')
    # ax.set_ylabel('Number of Commits')
    # ax.legend(title='Committers')
    # plt.xticks(rotation=45)  # Rotate date labels to prevent overlap
    # plt.tight_layout()  # Automatically adjust the layout
    # plt.savefig(f"committer_plot_total/{mnr.split('/')[0]}_{args.element}.png")



function createChangeMap(deep):
    changeMap = new ChangeMap()
    k1 = getAstNodeType()
    k2 = action.getName()

    if k1 is in ASTNodeMap.statements:
        changeMap.addOne(k1, k2)

    subActions = getSubActions()

    if subActions is not empty:
        if deep is true:
            for each subAction in subActions:
                subChangeMap = subAction.createChangeMap(true)
                changeMap.add(subChangeMap)
        else if changeMap is empty:
            for each subAction in subActions:
                subChangeMap = subAction.createChangeMap(false)
                if subChangeMap is not empty:
                    changeMap.add(subChangeMap)
                    break

    return changeMap