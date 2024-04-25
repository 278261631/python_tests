import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import median_filter, sobel
from skimage import feature

# 请确保这是您的 FITS 文件的实际路径
fits_file_path = r'E:/test_download/img_check/lines.fit'

# 使用 astropy 读取 FITS 文件
with fits.open(fits_file_path) as hdul:
    # 假设数据在第一个HDU中
    data = hdul[0].data
# 使用中值滤波器减少噪声
filtered_image = median_filter(data, size=5)

# 使用 Canny 算法检测边缘
edges = feature.canny(filtered_image, sigma=1.0)

sobel_x = sobel(filtered_image, axis=0, mode='constant')
sobel_y = sobel(filtered_image, axis=1, mode='constant')

# Calculate the direction of the gradient
directions = np.arctan2(sobel_y, sobel_x)

# 计算每个方向上的边缘强度
angle_bin_size = np.pi / 4
angle_bins = np.arange(-np.pi / 2, np.pi / 2 + angle_bin_size, angle_bin_size)
edge_histogram = np.histogram(directions, bins=angle_bins)[0]

# 找到边缘强度最高的方向，这可能是重影的方向
dominant_angle_idx = np.argmax(edge_histogram)
dominant_angle = angle_bins[dominant_angle_idx]

# 可视化原图、滤波图、边缘检测结果和方向
plt.figure(figsize=(20, 5))

plt.subplot(141)
plt.imshow(data, cmap='gray')
plt.title('Original FITS Image')

plt.subplot(142)
plt.imshow(filtered_image, cmap='gray')
plt.title('Filtered Image')

plt.subplot(143)
plt.imshow(edges, cmap='gray')
plt.title('Canny Edges')

plt.subplot(144)
plt.imshow(directions / np.pi * 180, cmap='hsv')
plt.title('Edge Directions')

plt.tight_layout()
plt.show()

# 根据主导方向，高亮可能的重影线条
ghost_edges = edges.copy()
influenced_directions = (directions > dominant_angle - np.pi / 4) & \
                       (directions < dominant_angle + np.pi / 4)
ghost_edges[influenced_directions] = 0

# 可视化重影边缘
plt.figure(figsize=(10, 5))
plt.imshow(ghost_edges, cmap='gray', vmin=0, vmax=1)
plt.title('Possible Ghosting Edges')
plt.axis('off')
plt.show()

