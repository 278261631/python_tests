import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# 假设我们有一些经纬度坐标
# 这里我们随机生成一些点作为示例
n_points = 100
np.random.seed(42)
longitudes = np.random.uniform(-180, 180, n_points)
latitudes = np.random.uniform(-90, 90, n_points)

# 将经纬度转换为距离矩阵
# 使用geodesic距离（大圆距离）
distances = np.zeros((n_points, n_points))
for i in range(n_points):
    for j in range(n_points):
        distances[i, j] = geodesic((latitudes[i], longitudes[i]), (latitudes[j], longitudes[j])).km / 10

# 计算距离矩阵的平方形式
distance_matrix = squareform(distances)

# 使用层次聚类算法
linked = linkage(distance_matrix, 'single')

# 绘制树状图
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, aspect='equal')  # 设置坐标轴比例为相等
dendrogram(linked, orientation='top', distance_sort='descending', show_leaf_counts=True, ax=ax)

# 显示距离信息
for i, d in enumerate(linked[:, 2]):
    ax.text(i, d, f"{d:.2f}", ha="center", va="center", color="blue")

# 添加解释性文字
plt.title('Hierarchical Clustering on a Sphere')
plt.xlabel('Sample Index')
plt.ylabel('Euclidean Distance')
plt.text(-2, 200, "The dendrogram shows the hierarchical clustering of points based on their latitude and longitude.\nThe distance at each node represents the linkage distance between clusters.", fontsize=10, color='grey', bbox=dict(facecolor='white', alpha=0.7))

# 显示图形
plt.show()