import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from geopy.distance import geodesic
import matplotlib.pyplot as plt


# 定义一个空的字典列表来存储数据
data_list = []

# 打开文件并逐行读取
in_line_count = 0
out_line_count = 0
with open('classify_fix.txt', 'r') as file:
    for line in file:
        # 移除行尾的换行符并按空格分割每行的数据
        parts = line.strip().split()
        in_line_count = in_line_count + 1
        # 确保分割后的数据部分正确
        if len(parts) == 8:
            out_line_count = out_line_count + 1
            # 提取数据并转换为适当的格式
            id_num, catalog, ra_hours, ra_minutes, ra_seconds, dec_degrees, dec_minutes, dec_seconds = parts

            ra_hours, ra_minutes, ra_seconds = map(float, [ra_hours, ra_minutes, ra_seconds])
            dec_degrees, dec_minutes, dec_seconds = map(float, [dec_degrees, dec_minutes, dec_seconds])

            # 计算并存储十进制的赤经和赤纬
            ra = (ra_hours + (ra_minutes / 60) + (ra_seconds / 3600)) * 15  # 转换为度
            dec = (dec_degrees + (dec_minutes / 60) + (dec_seconds / 3600))

            # 创建一个字典来存储当前行的数据
            entry = {
                'id': id_num,
                'catalog': catalog,
                'ra': ra,
                'dec': dec
            }

            # 将字典添加到列表中
            data_list.append(entry)
        else:
            print(line)
# assert (in_line_count == out_line_count)
if in_line_count > out_line_count:
    print("!!! 缺少行 !!! %d      %d - %d" % (in_line_count - out_line_count, in_line_count, out_line_count))
else:
    print("完整通过")

# 打印结果
for entry in data_list:
    print(entry)

