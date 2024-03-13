import math

import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# 假设我们有一些经纬度坐标
# 这里我们随机生成一些点作为示例
n_points = 9
np.random.seed(42)
longitudes = [7, 11, 12, 11, 20, 40, 80, 83, 180]
latitudes = [6, 11, 13, 10, 20, 40, 40, 43, 40]
# 地球的平均半径（单位：公里）
earth_radius_km = 6371.0
# 将经纬度转换为距离矩阵
# 使用geodesic距离（大圆距离）
distances = np.zeros((n_points, n_points))
for i in range(n_points):
    for j in range(n_points):
        distances[i, j] = geodesic((latitudes[i], longitudes[i]), (latitudes[j], longitudes[j])).km
        # 将大圆距离转换为角度（单位：弧度）
        distances_rad = distances[i, j] / earth_radius_km
        # 将弧度转换为度数
        distances[i, j] = distances_rad * (180 / math.pi)
        distances[i, j] = distances[i, j]

# 计算距离矩阵的平方形式
distance_matrix = squareform(distances)

# 使用层次聚类算法
linked = linkage(distance_matrix, 'single')

# 获取叶节点的顺序
leaves = leaves_list(linked)

# 绘制树状图
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, aspect='equal')  # 设置坐标轴比例为相等
dendrogram(linked, orientation='top', distance_sort='descending', show_leaf_counts=True, ax=ax)



n = n_points
original_indices = []


# 递归获取合并后簇包含的原始数据序号
def get_original_indices(merged_cluster_idx):
    # 获取合并后簇的子簇索引
    child1_idx = int(linked[merged_cluster_idx - n, 0])
    child2_idx = int(linked[merged_cluster_idx - n, 1])

    # 如果子簇索引小于 n，则它们是原始数据点
    if child1_idx < n:
        original_indices.append(child1_idx)
    else:
        get_original_indices(child1_idx)
    if child2_idx < n:
        original_indices.append(child2_idx)
    else:
        get_original_indices(child2_idx)

    # 打印当前节点的序号和包含的原始数据序号
    print(f"Cluster {i} includes original indices: {original_indices}")


# 显示距离信息
for i, d in enumerate(linked[:, 2]):
    ax.text(i*10, d, f"{d:.2f}", ha="center", va="center", color="blue")
    print(' %d  %f  ' % (i, d))
    # get_original_indices(i)

# 遍历 linked 矩阵的每一行
for i in range(len(linked)):
    # 提取每一行的四个值
    cluster_0_idx = linked[i, 0]
    cluster_1_idx = linked[i, 1]
    distance = linked[i, 2]
    num_points = linked[i, 3]

    # 打印每一行的四个值
    print(f"Row {i}:")
    print(f"  Cluster 0 Index: {cluster_0_idx}")
    print(f"  Cluster 1 Index: {cluster_1_idx}")
    print(f"  Distance: {distance}")
    print(f"  Number of Points: {num_points}")
    print()
    # get_original_indices()

# 假设 linked 是通过 linkage 函数得到的链接矩阵
# 假设 n 是原始数据点的数量


# 添加解释性文字
plt.title('Hierarchical Clustering on a Sphere')
plt.xlabel('Sample Index')
plt.ylabel('Euclidean Distance')

# 在图上显示每个点的坐标
ax2 = fig.add_subplot(111)  # 创建一个新的子图
ax2.axis('off')  # 关闭坐标轴
# for i, (lon, lat) in enumerate(zip(longitudes, latitudes)):
#     ax2.text(0.2 * i, 0.9, f"Point {i+1}: ({lon}, {lat})", bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="blue", lw=1))


# 初始化簇中心列表
cluster_centers = []

# # 遍历树状图的每个非叶节点
# for i in range(len(linked) - 1, 0, -1):
#     if linked[i, 0] != -1:  # 非叶节点
#         # 获取合并的两个簇的索引
#         cluster1_idx = int(linked[i, 0])
#         cluster2_idx = int(linked[i, 1])
#
#         # 获取每个簇包含的点的索引
#         cluster1_points = range(cluster1_idx, cluster2_idx)
#         cluster2_points = range(cluster2_idx, cluster2_idx + 1)
#
#         # 打印每个簇的索引和包含的点的坐标
#         print(f"Cluster {i}:")
#         for idx in cluster1_points:
#             print(f"  Point {idx}: Latitude {latitudes[idx]}, Longitude {longitudes[idx]}")
#         for idx in cluster2_points:
#             print(f"  Point {idx}: Latitude {latitudes[idx]}, Longitude {longitudes[idx]}")
#
#         # 打印合并的簇之间的距离
#         print(f"  Distance between clusters: {linked[i, 2]:.2f} km")
#         print()

# # 显示簇中心坐标
# for center in cluster_centers:
#     lat, lon = center
#     ax.text(lon, lat * 100, f"({lon:.2f}, {lat:.2f})", color="green", bbox=dict(facecolor='white', alpha=0.7))

# 调整子图布局


# 获取叶节点的索引



plt.tight_layout()

# 显示图形
plt.show()

