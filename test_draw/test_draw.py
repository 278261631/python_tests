# 从comtool.log 中提取 temp温度 并画出曲线
# 数据格式是 {"idx":104,"temp":14288,"c_t":-0.711277961730957,"c_r":63.076109886169432,"r":28,"o_t":37982}

import json
import matplotlib.pyplot as plt

# 读取文件并提取 temp 和 c_r 数据
def extract_temperatures(file_path):
    temperatures = []
    c_r_values = []
    with open(file_path, 'r') as file:
        for line in file:
            # 忽略不是json的行
            if not line.strip().startswith('{'):
                continue
            # 截取{} 之间的字符串, 包含{}
            line = line[line.find('{'):line.rfind('}')+1]

            try:
                data = json.loads(line)
                if data['temp'] < -50000:
                    data['temp'] = -50
                temperatures.append(data['temp']/1000)
                if data['c_r'] < -50000:
                    data['c_r'] = -50
                c_r_values.append(data['c_r'])
            except json.JSONDecodeError as error:
                print(f"Error parsing JSON: {line}")
                print(error)
                continue
            except Exception as error:
                print(f"Error parsing JSON: {line}")
                print(error)
                continue
    return temperatures, c_r_values

# 绘制温度和 c_r 曲线
def plot_temperatures(temperatures, c_r_values):
    plt.figure(figsize=(10, 5))
    plt.plot(temperatures, label='Temperature', color='b')
    plt.plot(c_r_values, label='c_r', color='r')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Temperature and c_r Curves')
    plt.legend()
    plt.grid(True)
    plt.show()

# 主函数
if __name__ == "__main__":
    file_path = 'comtool.log'
    temperatures, c_r_values = extract_temperatures(file_path)
    plot_temperatures(temperatures, c_r_values)