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

def merge_by_quarter(data_dict):
    """
    将键为人名，值为 {datetime.date: 次数} 的字典按季度合并次数。

    Args:
        data_dict (dict): 键为人名，值为 {datetime.date: 次数} 的字典。

    Returns:
        dict: 键为人名，值为按季度合并后的 { (年, 季度): 次数 } 的字典。
    """
    result = {}

    for person, date_counts in data_dict.items():
        quarter_dict = defaultdict(int)
        for date, count in date_counts.items():
            year = date.year
            quarter = (date.month - 1) // 3 + 1  # 计算季度
            quarter_key = (year, quarter)
            quarter_dict[quarter_key] += count
        result[person] = dict(quarter_dict)  # 转为普通字典

    return result

if __name__ == "__main__":
    VALID_CONFIGS = {
    # "MethodCircles": {"condition": "函数复杂度变化", "threshold": 10},
    "MethodRows": {"condition": "函数行数变化", "threshold": 30},
    # "FileRows": {"condition": "文件行数变化", "threshold": 2000},
    # "LineChars": {"condition": "行字符数变化", "threshold": 80},
    # "TryCatchNum":{"condition": "Try-Catch个数变化"},
    # "MethodNames":{"condition": "函数变量名变化"},
    }
    parser = argparse.ArgumentParser(description="argparse 处理命令行参数")
    # parser.add_argument("-e", "--element", type=str, default="LineChars")
    # args = parser.parse_args()
    # parser.add_argument("-c", "--condition", type=str, default=VALID_CONFIGS[args.element]['condition'])
    # parser.add_argument("-t", "--threshold", type=int, default=VALID_CONFIGS[args.element]['threshold'])
    parser.add_argument("-mnr", "--my_need_repo", type=list, default=[
    # "apache/dubbo",
    # "apache/kafka",
    # "apache/flink",
    # "apache/skywalking",
    # "apache/rocketmq",
    # "apache/shardingsphere",
    # "apache/hadoop",
    # "apache/pulsar",
    # "apache/druid",
    # "apache/zookeeper"
    "google/guava",
    "google/gson", 
    "google/ExoPlayer", 
    "google/dagger", 
    "google/guice", 
    "google/auto", 
    "google/tsunami-security-scanner",
    "google/error-prone", 
    "google/closure-compiler", 
    "google/nomulus"
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
    parser.add_argument("-r", "--rank", type=int, default=4)
    args = parser.parse_args()
    for elementArgu, value in VALID_CONFIGS.items():
        # parser.add_argument("-e", "--element", type=str, default="LineChars")
        # args = parser.parse_args()
        # parser.add_argument("-c", "--condition", type=str, default=VALID_CONFIGS[args.element]['condition'])
        # parser.add_argument("-t", "--threshold", type=int, default=VALID_CONFIGS[args.element]['threshold'])
        element = elementArgu
        condition = VALID_CONFIGS[element]['condition']
        threshold = VALID_CONFIGS[element]['threshold']
        
        need_plot_commit_p = defaultdict(lambda: defaultdict(int))
        need_plot_commit_n = defaultdict(lambda: defaultdict(int))
        need_plot_commit = defaultdict(lambda: defaultdict(int))
        
        for mnr in args.my_need_repo:
            # 输出解析结果
            file_path = 'circle/data_google_spring_wtc/%s/detail.txt' % element  # 你可以将此文件路径替换为实际文件路径
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
                match = re.match(r"(\d+) -> (\d+)", complexity_change)
                
                if match:
                    before = int(match.group(1))  # 提取前面的数字
                    after = int(match.group(2))   # 提取后面的数字
                # before, after = complexity_change.split(' -> ')
                # before = int(before)
                # after = int(after)
                
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
        
            author_with_commit_name = sorted(author_with_commit_num.items(), key=lambda x: x[1], reverse=True)     
            author_with_commit_p_name = sorted(author_with_commit_p_num.items(), key=lambda x: x[1], reverse=True)
            author_with_commit_n_name = sorted(author_with_commit_n_num.items(), key=lambda x: x[1], reverse=True)
            # need_plot_commit[mnr.split('/')[1]] = author_with_commit_name
            
            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts_p.items():
                if person == author_with_commit_p_name[0][0]:
                    need_plot_commit_p[mnr.split('/')[1]][person] = commits

            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts_n.items():
                if person == author_with_commit_n_name[0][0]:
                    need_plot_commit_n[mnr.split('/')[1]][person] = commits

            # 遍历每个提交人，绘制他们的提交次数随时间的变化
            for person, commits in commit_counts.items():
                if person == author_with_commit_name[0][0]:
                    need_plot_commit[mnr.split('/')[1]][person] = author_with_commit_name[0][1]    
            
        # # 准备绘图数据
        # plot_commit_p_no1 = {value.keys(): dict(value.values()) for _, value in need_plot_commit_p.items()}
        # fig, ax = plt.subplots(figsize=(10, 6))    
        
        person_commit = defaultdict(lambda: defaultdict(dict))
        for key, value in need_plot_commit_n.items():
            person, commits = list(value.items())[0]
            person_commit[key + '/' + person] = commits
        person_commit_quarter = merge_by_quarter(person_commit)
        plt.figure(figsize=(12, 6))

        # 获取全局的时间顺序
        all_quarters = set()
        for quarter_counts in person_commit_quarter.values():
            all_quarters.update(quarter_counts.keys())
        all_quarters = sorted(all_quarters)  # 按 (year, quarter) 排序

        # 转换为字符串形式
        x_labels = [f"{year}-Q{quarter}" for year, quarter in all_quarters]

        for person, quarter_counts in person_commit_quarter.items():
            # 将数据映射到全局顺序上，缺失的时间填充为 0
            counts = [quarter_counts.get(q, 0) for q in all_quarters]
            
            # 绘制折线图
            plt.plot(x_labels, counts, marker='o', label=person)

        # 设置图例、标题和轴标签
        plt.title(f"Quarterly statistics of {elementArgu}", fontsize=30)
        plt.xlabel("Quarter", fontsize=30)
        plt.ylabel("Counts", fontsize=30)
        plt.tick_params(axis="x", labelsize=16)
        plt.tick_params(axis="y", labelsize=16)
        plt.legend(loc='upper left', fontsize=12)
        plt.xticks(rotation=45)  # X 轴标签旋转以便显示
        plt.tight_layout()      # 调整布局以防标签重叠
        plt.grid(True)          # 添加网格线
            
        # counts = [commits[date] for date in dates]
        # ax.plot(dates, counts, label=person, marker='o')
        # ax.set_legend("{} {}".format(person, author_with_commit_num[person]))
        
        # # Set the title, labels, and other properties of the plot
        # ax.set_title(f'Number of Commits Increasing {args.element} Over Time')
        # ax.set_xlabel('Date')
        # ax.set_ylabel('Number of Commits')
        # ax.legend(title='Committers')
        # plt.xticks(rotation=45)  # Rotate date labels to prevent overlap
        # plt.tight_layout()  # Automatically adjust the layout
        plt.savefig(f"committer_plot_committer_n/{mnr.split('/')[0]}_{element}.png", dpi=600, bbox_inches='tight')