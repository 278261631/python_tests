import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import binary_dilation, generate_binary_structure
from skimage import feature, io, morphology, measure

# 请确保这是您的 FITS 文件的实际路径
fits_file_path = r'E:/test_download/img_check/lines.fit'

# 使用 astropy 读取 FITS 文件
with fits.open(fits_file_path) as hdul:
    # 假设数据在第一个HDU中
    data = hdul[0].data

# 使用 Canny 算法检测边缘
edges = feature.canny(data, sigma=2.0)

# 生成膨胀用的圆形结构元素
radius = 2
structure = generate_binary_structure(2, radius)

# 对边缘进行膨胀，增强线条
dilated_edges = binary_dilation(edges, structure=structure)


# 标记连通域
label_image = morphology.label(dilated_edges)

# 计算每个连通域的属性
props = measure.regionprops(label_image)

# 过滤出周长大于某个阈值的连通域，作为长线条
# 例如，我们可以选取周长大于某个固定值的线条
min_perimeter = 1000
long_edges = [prop for prop in props if prop.perimeter > min_perimeter]
print(f' edges {len(dilated_edges)}    {len(long_edges)}')

# # 可视化原图和膨胀后的边缘
# plt.figure(figsize=(12, 6))
# plt.subplot(1, 2, 1)
# plt.imshow(data, cmap='gray')
# plt.title('Original Image')
#
# plt.subplot(1, 2, 2)
# plt.imshow(dilated_edges, cmap='gray')
# plt.title('Dilated Edges')
#
# # 显示图像
# plt.tight_layout()
# plt.show()

for edge in long_edges:
    # 创建一个与原图同样大小的零数组来标记长线条
    long_edge_img = np.zeros_like(data, dtype=bool)
    # 在新图像中标记长线条的连通域
    long_edge_img[label_image == edge.label] = True
    plt.figure()
    plt.imshow(long_edge_img, cmap='gray')
    plt.title(f'Long Edge #{edge.label}')
    plt.axis('off')
    print(long_edge_img)

# 显示所有长线条
plt.show()
