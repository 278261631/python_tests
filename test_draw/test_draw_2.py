import json
import matplotlib.pyplot as plt
import time

# 读取文件并提取 temp 和 c_r 数据
def extract_temperatures(file):
    temperatures = []
    c_r_values = []
    lines = file.readlines()
    for line in lines:
        # 忽略不是json的行
        if not line.strip().startswith('{'):
            continue
        # 截取{} 之间的字符串, 包含{}
        start = line.find('{')
        end = line.rfind('}') + 1
        if start == -1 or end == -1:
            continue
        json_str = line[start:end]

        try:
            data = json.loads(json_str)
            if data['temp'] < -50000:
                data['temp'] = -50000
            temperatures.append(data['temp']/1000)
            if data['c_r'] < 0:
                data['c_r'] = -20
            c_r_values.append(data['c_r'])
        except json.JSONDecodeError as error:
            print(f"Error parsing JSON: {json_str}")
            print(error)
            continue
        except Exception as error:
            print(f"Error parsing JSON: {json_str}")
            print(error)
            continue
    return temperatures, c_r_values

# 主函数
if __name__ == "__main__":
    file_path = 'comtool.log'
    # 打开文件并保持指针在末尾
    file = open(file_path, 'r')
    # file.seek(0, 2)  # 移动到文件末尾

    # 提取初始数据
    temperatures, c_r_values = extract_temperatures(file)
    # 初始化图表
    plt.ion()  # 开启交互模式
    fig, ax = plt.subplots()
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_title('Temperature and c_r Curves')
    ax.grid(True)
    line_temp, = ax.plot(temperatures, label='Temperature', color='b')
    line_c_r, = ax.plot(c_r_values, label='c_r', color='r')
    ax.legend()
    # 设置图表窗口尺寸为 800*1000 像素
    plt.gcf().set_size_inches(14, 8)

    while True:
        # 如果窗口关闭就退出循环
        if not plt.fignum_exists(fig.number):
            break
        # 读取新增加的行
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(1)  # 没有新数据时休眠
            file.seek(where)
            continue
        # 处理新读取的行
        if not line.strip().startswith('{'):
            continue
        start = line.find('{')
        end = line.rfind('}') + 1
        if start == -1 or end == -1:
            continue
        json_str = line[start:end]

        try:
            data = json.loads(json_str)
            if data['temp'] < -50000:
                data['temp'] = -50000
            temperatures.append(data['temp']/1000)
            if data['c_r'] < 0:
                data['c_r'] = -20
            c_r_values.append(data['c_r'])
            # 更新图表数据
            line_temp.set_xdata(range(len(temperatures)))
            line_temp.set_ydata(temperatures)
            line_c_r.set_xdata(range(len(c_r_values)))
            line_c_r.set_ydata(c_r_values)
            # 调整 x 轴范围
            ax.set_xlim(len(temperatures)-1000, len(temperatures)+500)
            # 调整 y 轴范围为 -2 到 最后1000个temperatures的最大值加5
            # ax.set_ylim(-12, max(temperatures[-1000:])+5)
            ax.set_ylim(-52, 100)
            # ax.set_ylim(-2, 25)
            # 重新绘制图表
            fig.canvas.draw()
            fig.canvas.flush_events()
        except json.JSONDecodeError as error:
            print(f"Error parsing JSON: {json_str}")
            print(error)
            continue
        except Exception as error:
            print(f"Error parsing JSON: {json_str}")
            print(error)
            continue