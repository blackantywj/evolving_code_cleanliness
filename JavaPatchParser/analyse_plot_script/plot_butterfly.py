import csv
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

plt.rcParams['font.family'] = 'Times New Roman'
# 存储每列的数据
data = {
    "type": [],
    "repository": [],
    "commitSha": [],
    "author": [],
    "committer": [],
    "fileName": [],
    "methodName": [],
    "direction": [],
    "statement": [],
    "INS": [],
    "DEL": [],
    "MOV": [],
    "UPD": []
}

if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser(description="argparse 处理命令行参数")
    parser.add_argument("-a", "--argument", type=str, default="FileRows")
    parser.add_argument("-c", "--community", type=str, default="google")
    
    args = parser.parse_args()
    
    # 读取 CSV 文件
    file_path = f'circle/data_google_spring_statement/{args.argument}/analyse.csv'  # 替换为你的文件路径
    # data = pd.read_csv(file_path)
    # print(data)
    
    # 初始化字典
    positive_summary = defaultdict(lambda: {'INS': 0, 'DEL': 0, 'MOV': 0, 'UPD': 0})
    negative_summary = defaultdict(lambda: {'INS': 0, 'DEL': 0, 'MOV': 0, 'UPD': 0})

    # 读取 CSV 文件
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if args.community == "apache":
                if row['type'] == '汇总':  # 只处理 "汇总" 数据
                    statement = row['statement']
                    direction = row['direction']
                    ins = int(row['INS'])
                    delete = int(row['DEL'])
                    move = int(row['MOV'])
                    update = int(row['UPD'])

                    # 累加数据
                    if direction == '正向':
                        positive_summary[statement]['INS'] += ins
                        positive_summary[statement]['DEL'] += delete
                        positive_summary[statement]['MOV'] += move
                        positive_summary[statement]['UPD'] += update
                    elif direction == '反向':
                        negative_summary[statement]['INS'] += ins
                        negative_summary[statement]['DEL'] += delete
                        negative_summary[statement]['MOV'] += move
                        negative_summary[statement]['UPD'] += update
                        
            elif args.community == "google":
                if ('repository' not in row) or ('repository' in row and "google" not in row['repository']) or row['commitSha'] == '':  # 只处理 "汇总" 数据
                    continue
                direction = row['direction']
                statement = row['statement']
                ins = int(row['INS'])
                delete = int(row['DEL'])
                move = int(row['MOV'])
                update = int(row['UPD'])

                # 根据 direction 选择对应的字典
                if direction == '正向':
                    target_dict = positive_summary
                elif direction == '反向':
                    target_dict = negative_summary
                else:
                    continue  # 跳过无效数据

                # 累加 statement 对应的 INS/DEL/MOV/UPD
                if statement not in target_dict:
                    target_dict[statement] = {'INS': 0, 'DEL': 0, 'MOV': 0, 'UPD': 0}
                
                target_dict[statement]['INS'] += ins
                target_dict[statement]['DEL'] += delete
                target_dict[statement]['MOV'] += move
                target_dict[statement]['UPD'] += update
                
            elif args.community == "spring":
                if ('repository' not in row) or ('repository' in row and "spring" not in row['repository']) or row["commitSha"] == '':  # 只处理 "汇总" 数据
                    continue
                direction = row['direction']
                statement = row['statement']
                ins = int(row['INS'])
                delete = int(row['DEL'])
                move = int(row['MOV'])
                update = int(row['UPD'])

                # 根据 direction 选择对应的字典
                if direction == '正向':
                    target_dict = positive_summary
                elif direction == '反向':
                    target_dict = negative_summary
                else:
                    continue  # 跳过无效数据

                # 累加 statement 对应的 INS/DEL/MOV/UPD
                if statement not in target_dict:
                    target_dict[statement] = {'INS': 0, 'DEL': 0, 'MOV': 0, 'UPD': 0}
                
                target_dict[statement]['INS'] += ins
                target_dict[statement]['DEL'] += delete
                target_dict[statement]['MOV'] += move
                target_dict[statement]['UPD'] += update
                
    # 获取所有语句类型的并集
    statements = set(positive_summary.keys()).union(set(negative_summary.keys()))

    # 初始化统一的字典，缺失的值填充为0
    positive_data_uniform = {
        stmt: {cat: positive_summary.get(stmt, {}).get(cat, 0) for cat in ['INS', 'DEL', 'MOV', 'UPD']}
        for stmt in statements
    }

    negative_data_uniform = {
        stmt: {cat: negative_summary.get(stmt, {}).get(cat, 0) for cat in ['INS', 'DEL', 'MOV', 'UPD']}
        for stmt in statements
    }

    # # 语句类型列表
    # statements = sorted(statements)  # 排序便于图表展示
    
    total_counts = {
    stmt: sum(positive_data_uniform[stmt].values()) + sum(negative_data_uniform[stmt].values())
    for stmt in statements
    }
    sorted_statements = sorted(total_counts.keys(), key=lambda x: total_counts[x])

    
    # 定义四种情况的颜色和标签
    categories = ["INS", "DEL", "MOV", "UPD"]
    colors = ["#91CCC0", "#EC6E66", "#F7AC53", "#6699CC"]

    # 数据准备
    positive_values = {cat: [positive_data_uniform[stmt][cat] for stmt in sorted_statements] for cat in categories}
    negative_values = {cat: [-negative_data_uniform[stmt][cat] for stmt in sorted_statements] for cat in categories}

    # 创建水平堆叠条形图
    fig, ax = plt.subplots(figsize=(10, 6))

    # 累积绘制每个类别
    for i, cat in enumerate(categories):
        ax.barh(sorted_statements, positive_values[cat], color=colors[i], label=f"{cat}", left=np.sum(
            [positive_values[c] for c in categories[:i]], axis=0))
        ax.barh(sorted_statements, negative_values[cat], color=colors[i], left=np.sum(
            [negative_values[c] for c in categories[:i]], axis=0))

    # 添加垂直分界线
    ax.axvline(x=0, color="black", linewidth=1, linestyle="--")

    # 图例、标签和标题
    ax.set_xlabel("Counts", fontsize=16)
    ax.set_title(f"{args.community}-{args.argument}", fontsize=16)
    ax.legend(loc="upper right", fontsize=12)
    
    # 添加正负区域的文本标签
    # plt.text(-max(total_counts.values()) * 0.8, 0.5, "Negative", fontsize=16, color="black", ha="right")
    # plt.text(max(total_counts.values()) * 0.3, 0.5, "Positive", fontsize=16, color="black", ha="center")
    
    # 调整 x 轴刻度标签：负方向改为正数
    xticks = ax.get_xticks()
    ax.set_xticks(xticks)
    ax.set_xticklabels([abs(int(tick)) for tick in xticks], fontsize=12)
    # # 创建嵌套插图（显示总数较小的部分）
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    # 选择小数据的子集（最后两项）
    subset_statements = sorted_statements[:7]
    subset_positive = {cat: [positive_data_uniform[stmt][cat] for stmt in subset_statements] for cat in categories}
    subset_negative = {cat: [-negative_data_uniform[stmt][cat] for stmt in subset_statements] for cat in categories}

    # 插入子图
    ax_inset = inset_axes(ax, width="40%", height="40%", loc="lower center", borderpad=2)
    for i, cat in enumerate(categories):
        ax_inset.barh(
            subset_statements,
            subset_negative[cat],
            color=colors[i],
            left=np.sum([subset_negative[c] for c in categories[:i]], axis=0),
        )
        ax_inset.barh(
            subset_statements,
            subset_positive[cat],
            color=colors[i],
            left=np.sum([subset_positive[c] for c in categories[:i]], axis=0),
        )

    # 子图添加垂直分界线
    ax_inset.axvline(x=0, color="black", linewidth=1, linestyle="--")

    # 子图调整 x 轴刻度标签为正数
    inset_xticks = ax_inset.get_xticks()
    ax_inset.set_xticks(inset_xticks)
    ax_inset.set_xticklabels([abs(int(tick)) for tick in inset_xticks], fontsize=8)

    # 子图格式调整
    # ax_inset.set_title("Focused View", fontsize=10)
    ax_inset.tick_params(axis="y", labelsize=10)
    ax_inset.tick_params(axis="x", labelsize=6)

    # 添加右侧 y 轴标签
    ax_inset.yaxis.tick_right()  # 移动 y 轴刻度到右侧
    ax_inset.yaxis.set_label_position("right")  # 设置 y 轴标签在右侧

    total_counts_sub = {k: total_counts[k] for k in subset_statements}
    max_abs_value_1 = max(abs(val) for val in list(total_counts_sub.values()))  # 获取正负数据的最大值
    ax_inset.set_xlim(-max_abs_value_1, max_abs_value_1)  # 设置对称范围
    
    # 设置 x 轴范围以保证正负方向对称
    # 找出两个字典中的最大值
    max_value = 0
    max_key = None
    max_sub_key = None
    source_dict = None  # 用于记录最大值来自哪个字典

    # 遍历第一个字典
    for key, sub_dict in positive_data_uniform.items():
        for sub_key, value in sub_dict.items():
            if value > max_value:
                max_value = value

    # 遍历第二个字典
    for key, sub_dict in negative_data_uniform.items():
        for sub_key, value in sub_dict.items():
            if value > max_value:
                max_value = value
                
    max_abs_value = max(abs(val) for val in total_counts.values())  # 获取正负数据的最大值
    ax.set_xlim(-max_abs_value, max_abs_value - 2)  # 设置对称范围
    ax.tick_params(axis="y", labelsize=18)
    # ax.set_ylim(-10, 10)
    # 美化
    # 手动调整图形边距（备用方法）
    # plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # 完全去除四周的空白
    plt.tight_layout()
    
    # 显示图表
    plt.savefig(f'{args.community}_butterfly_{args.argument}_test.png', dpi=1000, bbox_inches="tight")
        
