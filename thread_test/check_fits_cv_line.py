import os

import cv2
import matplotlib
import numpy as np
import sep
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle
from photutils.detection import DAOStarFinder
from skimage.color import rgb2gray


matplotlib.use('TkAgg')
from skimage import io, filters, measure, color, morphology, exposure, feature

import cv2
import numpy as np

# 读取图像
# image = cv2.imread(f'e:/fix_data/bad1_dif.png', cv2.IMREAD_GRAYSCALE)
# image = cv2.imread(f'e:/fix_data/good_dif.png', cv2.IMREAD_GRAYSCALE)
image = cv2.imread(f'e:/fix_data/ok-bad_foucs_dif.png', cv2.IMREAD_GRAYSCALE)

# 应用滤波器去除噪声
smoothed_image = cv2.GaussianBlur(image, (9, 9), 2)
# 使用双边滤波器去除噪声
# smoothed_image = cv2.bilateralFilter(image, 9, 75, 75)

# 或者使用非线性去噪算法
# denoised_image = cv2.fastNlMeansDenoising(smoothed_image, None, 10, 7, 21)

# 边缘检测，例如使用Canny算法
edges = cv2.Canny(smoothed_image, 50, 150)

# 膨胀操作
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))  # 定义结构元素
dilated_edges = cv2.dilate(edges, kernel, iterations=1)



# 寻找膨胀后的轮廓
contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 初始化长宽比总和和轮廓数量
aspect_ratio_sum = 0
contour_count = 0

# 遍历所有轮廓
aspect_ratios = []
line_count = 0
for contour in contours:
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)
    # print(f'--  {x}  {y}  {w}  {h}')
    # 计算长宽比，跳过高度为0的情况以避免除以零的错误

    if h != 0 and w != 0:
        big_v = w if w > h else h
        small_v = w if w < h else h
        aspect_ratio = float(big_v) / small_v
        aspect_ratio_sum += aspect_ratio
        contour_count += 1
        if aspect_ratio > 2:
            line_count = line_count+1
        aspect_ratios.append(aspect_ratio)
if aspect_ratios:
    median_aspect_ratio = np.median(aspect_ratios)
    print(f"宽高比的中位数: {median_aspect_ratio:.2f}")
else:
    print("没有有效的宽高比数据。")
print(f'--  len:{len(contours)}  mean:{aspect_ratio_sum/contour_count}  {line_count}')

# 计算平均长宽比
if contour_count > 0:
    average_aspect_ratio = aspect_ratio_sum / contour_count
    print(f"所有轮廓的长宽比平均值: {average_aspect_ratio:.2f}")

    # 判断平均长宽比是否大于3
    if average_aspect_ratio > 5:
        print("平均长宽比大于3，图像中可能存在条带形状分布")
    else:
        print("平均长宽比不大于3，图像中可能不存在条带形状分布")
else:
    print("没有找到有效的轮廓")


image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

# 创建图像的matplotlib图形
fig, ax = plt.subplots(figsize=(image.shape[1]/100, image.shape[0]/100))
ax.imshow(image_rgb, extent=[0, image.shape[1], image.shape[0], 0])

# 遍历所有轮廓并绘制
for contour in contours:
    # 提取轮廓的所有点的X和Y坐标
    points = contour.reshape(-1, 2)
    xs = points[:, 1]
    ys = points[:, 0]

    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(points)

    big_v = w if w > h else h
    small_v = w if w < h else h
    aspect_ratio = float(big_v) / small_v

    # 根据长宽比绘制不同颜色的轮廓
    if aspect_ratio > 3:
        ax.plot(ys, xs, color='green')  # 长宽比大于2的轮廓用绿色绘制
    else:
        ax.plot(ys, xs, color='red')   # 其他轮廓用红色绘制

# 显示图像
# plt.show()

plt.savefig(f'e:/fix_data/red_green.png', dpi=100, format='png', bbox_inches='tight')
plt.close(fig)
