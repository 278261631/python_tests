import matplotlib.pyplot as plt
import numpy as np
import time

# 初始化数据
x = np.arange(0, 10, 0.1)
y = np.random.rand(len(x))

# 创建图形和轴
plt.ion()  # 开启交互模式
fig, ax = plt.subplots()
line, = ax.plot(x, y)

# 设置图形属性
ax.set_ylim(0, 1)  # 设置y轴范围
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
ax.set_title('实时更新随机数据')

# 持续更新数据
while True:
    # 生成新的随机数据
    y = np.random.rand(len(x))

    # 更新数据
    line.set_ydata(y)

    # 重新绘制图形
    fig.canvas.draw()
    fig.canvas.flush_events()

    # 暂停一段时间
    time.sleep(0.1)