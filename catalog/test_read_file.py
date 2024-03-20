# 假设文件名为 'hip_numbers.txt'
from catalog.test_search_hip3 import query_hip

file_name = 'hip.txt'

# 用于存储解析后的星座和HIP编号的字典
hip_data = {}

# 逐行读取文件
with open(file_name, 'r') as file:
    for line in file:
        # 移除行尾的换行符并分割字符串
        parts = line.strip().split('-')
        if len(parts) == 3:
            name, constellation, hip_list_str = parts
            # 将HIP编号字符串转换为实际的列表
            hip_list = eval(hip_list_str)
            # 将星座和HIP编号列表存储到字典中
            hip_data[name] = hip_list

# 遍历字典并打印结果
for constellation, hip_list in hip_data.items():
    print(f"星座: {name} {constellation}")
    for hip in hip_list:
        print(f"  HIP编号: {hip}")
    print()  # 打印空行以分隔星座


# 遍历字典并打印结果
for name, hip_list in hip_data.items():
    print(f'{{"{name}":{hip_list}}}')

for name, hip_list in hip_data.items():
    hip_cord_data = {name: []}
    for line in hip_list:
        line_data = []
        for star in line:
            star_cord = query_hip(star)
            star_cord = [star_cord.ra.value, star_cord.dec.value]
            # star_cord = [0, 1]
            line_data.append(star_cord)
        hip_cord_data[name].append(line_data)
    print(hip_cord_data)



