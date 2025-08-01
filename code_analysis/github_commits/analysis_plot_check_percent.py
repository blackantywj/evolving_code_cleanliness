import json 
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.dates as mdates
from datetime import datetime

if __name__ == "__main__":
    fileName = "google.json"
    with open(fileName, 'r') as file:
        data = json.load(file)

    # #     print(data)
    # # # 初始化一个默认字典来存储每月统计结果
    # monthly_data = defaultdict(lambda: defaultdict(int))

    # # 数据按月统计
    # for project, records in data.items():
    #     for date_str, value in records.items():
    #         # 将日期字符串解析为 datetime 对象
    #         date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    #         # 按月份统计
    #         month_key = date_obj.strftime('%Y-%m')
    #         monthly_data[project][month_key] += value

    # # 可视化：
    # # 按项目绘制每月统计数据
    # fig, ax = plt.subplots(figsize=(10, 6))

    # for project, monthly_records in monthly_data.items():
    #     # 按时间排序月份
    #     sorted_months = sorted(monthly_records.keys())
    #     # 提取月份和对应值
    #     months = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
    #     values = [monthly_records[month] for month in sorted_months]
    #     # 绘制折线图
    #     ax.plot(months, values, marker='o', label=project)

    # # 格式化 x 轴为月份
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    # plt.xticks(rotation=45)

    # # 添加图例、标题和轴标签
    # ax.legend()
    # plt.title('Monthly Statistics per Project')
    # plt.xlabel('Month')
    # plt.ylabel('Value')
    # plt.grid(True)

    # # 展示图表
    # plt.tight_layout()
    # name = fileName.split(".")[0]
    # plt.savefig(f"{name}_checkTime.png", dpi=800)

    # 初始化一个默认字典来存储每月统计结果
    combined_monthly_data = defaultdict(int)

    # 数据按月合并统计
    for project, records in data.items():
        for date_str, value in records.items():
            # 将日期字符串解析为 datetime 对象
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # 按月份统计
            month_key = date_obj.strftime('%Y-%m')
            combined_monthly_data[month_key] += value

    # 可视化：
    # 按时间排序月份
    sorted_months = sorted(combined_monthly_data.keys())
    months = [datetime.strptime(month, '%Y-%m') for month in sorted_months]
    values = [combined_monthly_data[month] for month in sorted_months]

    fig, ax = plt.subplots(figsize=(10, 6))

    # 绘制折线图
    ax.plot(months, values, marker='o', label='Combined Data')

    # 格式化 x 轴为月份
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)

    # 添加图例、标题和轴标签
    ax.legend()
    plt.title('Monthly Combined Statistics')
    plt.xlabel('Month')
    plt.ylabel('Value')
    plt.grid(True)

    # 展示图表
    plt.tight_layout()
    name = fileName.split(".")[0]
    plt.savefig(f"{name}_checkTime.png", dpi=800)
