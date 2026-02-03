import json
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Times New Roman'

# 从文件读取数据
all_data = []
project = ['google', 'apache', 'spring-projects']
argument = 'LineChars'
for i in project:
    with open(f'{argument}_{i}.json', 'r') as f:
        data = json.load(f)
        all_data.append(data)

# 绘制折线图
fig, ax = plt.subplots(figsize=(10, 6))

# 颜色列表
colors = ['#91CCC0', '#EC6E66', '#F7AC53']
for i, data in enumerate(all_data):
    months = data['months']
    values1 = list(data['values1'].values())
    values2 = list(data['values2'].values())
    
    # 绘制两组数据
    ax.plot(months, values2, label=f'{project[i]}-S', color=colors[i], alpha=0.7, linewidth=2, marker='o')
    # ax.plot(months, values1, label=f'{project[i]}-D', color=colors[i], alpha=1.0, linewidth=2, linestyle='--', marker='x')

# 添加标签、标题和图例
ax.set_xlabel('Year-Month', fontsize=40)
ax.set_ylabel('Counts', fontsize=40)
ax.set_title(f'{argument}_P', fontsize=40)
ax.legend(loc='upper right', fontsize=16)
# ax.legend.get_frame().set_alpha(0.5)  # 设置图例的透明度为0.5
# 调整 X 轴刻度
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

# 显示网格
ax.grid(visible=True, linestyle='--', alpha=0.5)

# 显示图表
plt.tight_layout()
plt.savefig(f'{argument}_P.png', dpi=500)        
