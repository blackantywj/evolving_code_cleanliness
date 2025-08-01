import matplotlib.pyplot as plt

# 数据
categories = ['Code line lengths', 'LOCs of files', 'LOCs of functions', 'Cyclomatic complexity']
positive_values = [1, 3, 222, 1]
negative_values = [0, 0, 45, 0]

# 绘制条形图
fig, ax = plt.subplots()

# 正向条形图
ax.barh(categories, positive_values, color='green', label='Maintain (P)')
# 负向条形图
ax.barh(categories, negative_values, left=positive_values, color='red', label='Maintain (N)')

# 添加标签和标题
ax.set_xlabel('Values')
ax.set_ylabel('Categories')
ax.set_title('Code Metrics Analysis')

# 添加网格线
ax.grid(True)

# 显示图例
ax.legend()

# 显示图表
plt.savefig("./statistic/1.png", dpi=800)