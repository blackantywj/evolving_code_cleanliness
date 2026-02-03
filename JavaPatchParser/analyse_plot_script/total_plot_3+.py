# import json
# import matplotlib.pyplot as plt

# plt.rcParams['font.family'] = 'Times New Roman'

# # 从文件读取数据
# all_data = []
# project = ['google', 'apache', 'spring-projects']
# argument = 'TryCatchNum'
# for i in project:
#     with open(f'{argument}_{i}.json', 'r') as f:
#         data = json.load(f)
#         all_data.append(data)


# # 绘制折线图
# fig, ax = plt.subplots(figsize=(10, 6))

# # 颜色列表
# colors = ['#91CCC0', '#EC6E66', '#F7AC53']
# for i, data in enumerate(all_data):
#     months = data['months']
#     values1 = list(data['values1'].values())
#     values2 = list(data['values2'].values())
#     values3 = list(data['values3'].values())
    
#     # 绘制两组数据
#     ax.plot(months, values2, label=f'{project[i]}-↑', color=colors[i], alpha=1.0, linewidth=2, marker='o')
#     ax.plot(months, values1, label=f'{project[i]}--', color=colors[i], alpha=1.0, linewidth=2, linestyle='--', marker='x')
#     ax.plot(months, values3, label=f'{project[i]}-↓', color=colors[i], alpha=1.0, linewidth=2, linestyle='-.', marker='*')
    
    
# # 添加标签、标题和图例
# ax.set_xlabel('Month-Year', fontsize=12)
# ax.set_ylabel('Counts', fontsize=12)
# ax.set_title(f'{argument}', fontsize=14)
# ax.legend(loc='upper right')
# # ax.legend.get_frame().set_alpha(0.5)  # 设置图例的透明度为0.5
# # 调整 X 轴刻度
# plt.xticks(rotation=45, fontsize=10)

# # 显示网格
# ax.grid(visible=True, linestyle='--', alpha=0.5)

# # 显示图表
# plt.tight_layout()
# plt.savefig(f'{argument}.png', dpi=500)        


import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# 设置字体
plt.rcParams['font.family'] = 'Times New Roman'

# 从文件读取数据
all_data = []
project = ['google', 'apache', 'spring-projects']
argument = 'VariableNames'

for i in project:
    with open(f'{argument}_{i}.json', 'r') as f:
        data = json.load(f)
        all_data.append(data)

# 绘制折线图
fig, ax1 = plt.subplots(figsize=(10, 6))

# 颜色列表
colors = ['#91CCC0', '#EC6E66', '#F7AC53']

# 遍历数据并绘制
for i, data in enumerate(all_data):
    months = data['months']
    # values1 = list(data['values1'].values())
    values2 = list(data['values2'].values())
    values3 = list(data['values3'].values())
    # values4 = list(data['values4'].values())

    # 绘制主轴上的 values1
    ax1.plot(months, values2, label=f'{project[i]}/S', color=colors[i], alpha=1.0, linewidth=2, marker='o')
    ax1.plot(months, values3, label=f'{project[i]}/D', color=colors[i], alpha=1.0, linewidth=2, linestyle='--', marker='x')
# # 创建副轴
# ax2 = ax1.twinx()

# # 绘制副轴上的 values2 和 values3
# for i, data in enumerate(all_data):
#     months = data['months']
#     values1 = list(data['values1'].values())
#     values4 = list(data['values4'].values())

#     ax2.plot(months, values1, label=f'{project[i]}/-(+)', color=colors[i], alpha=0.3, linewidth=2, linestyle='--', marker='o')
#     ax2.plot(months, values4, label=f'{project[i]}/-(-)', color=colors[i], alpha=0.3, linewidth=2, linestyle='-.', marker='*')

# 添加标签和标题
ax1.set_xlabel('Year-Month', fontsize=30)
ax1.set_ylabel('Counts', fontsize=30, color='black')
# ax2.set_ylabel('Counts (↑/↓)', fontsize=12, color='black')
ax1.set_title(f'{argument}', fontsize=30)

# # 调整 X 轴刻度
# plt.xticks(rotation=60, fontsize=1)  # 标签旋转 45° 并右对齐
ax1.set_xticks(range(len(months)))  # 确保刻度与数据对齐
ax1.set_xticklabels(months, rotation=45, fontsize=16, ha='right')  # 旋转标签并右对齐

# 显示网格
ax1.grid(visible=True, linestyle='--', alpha=0.5)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=7.5)
ax1.legend(lines1, labels1, loc='upper left', fontsize=16)
# 设置 y 轴刻度为整数
ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
# ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

# 调整布局并保存图像
plt.tight_layout()
plt.savefig(f'{argument}.png', dpi=600)
plt.show()
