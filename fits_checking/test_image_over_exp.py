import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import gaussian_filter
from skimage import exposure
from skimage.exposure import histogram
from skimage.util import img_as_float

# 替换为你的 FITS 文件路径
fits_file_path = r'E:/test_download/img_check/lines.fit'

# 使用 astropy 读取 FITS 文件
with fits.open(fits_file_path) as hdul:
    # 假设数据在第一个 HDU 中
    data = hdul[0].data


# 计算直方图
hist, bin_edges = histogram(data)
print(f'{len(hist)}   {len(bin_edges)}')

# 计算直方图的累积分布函数 (CDF)
cdf = np.cumsum(hist) / np.sum(hist)

# 可视化直方图和累积分布函数
plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
plt.imshow(data, cmap='gray')
plt.title('Original FITS Image')

plt.subplot(1, 2, 2)
plt.plot(bin_edges[0:], cdf * 100)  # CDF 表示累积百分比
plt.xlabel('Pixel Value')
plt.ylabel('Cumulative Percentage')
plt.title('Cumulative Distribution Function')

plt.tight_layout()
plt.show()

# 检查直方图是否存在过曝的迹象
# 通常，如果大量像素集中在直方图的右侧，可能表明图像过曝
# 这里我们检查超过一定百分比（如 95%）的像素是否集中在最高的 5% 的 bin 中
threshold_percentage = 95
threshold_index = int(threshold_percentage / 100 * len(cdf))
is_overexposed = cdf[-1] - cdf[threshold_index] > 0.9  # 阈值可能需要调整

print(f"The image is {'---- overexposed' if is_overexposed else '++++ not overexposed'} .")


# # 将图像转换为 float 类型，范围在 0 到 1 之间
# gray_image_float = img_as_float(data)
#
# # 使用 skimage 的 is_low_contrast 函数检测图像是否低对比度
# low_contrast_image = exposure.is_low_contrast(gray_image_float, fraction_threshold=0.04)
#
# # 可视化原图和直方图
# plt.figure(figsize=(14, 7))
#
# plt.subplot(1, 2, 1)
# plt.imshow(gray_image_float, cmap='gray')
# plt.title('Original Image')
#
# plt.subplot(1, 2, 2)
# plt.hist(gray_image_float.flatten(), bins=10, range=(0, 1), histtype='stepfilled')
# plt.title('Histogram')
#
# plt.tight_layout()
# plt.show()
#
# # 检测结果
# print(f"The image is {'---  low contrast' if low_contrast_image else '+++ not low contrast'} ")
#
# # 检查直方图的分布，如果大部分像素集中在亮度较高的区间，可能过度曝光
# histogram, bin_edges = np.histogram(gray_image_float, bins=10, range=(0, 1))
# print(histogram)
# print(bin_edges)
# cumulative_distribution = np.cumsum(histogram) / np.sum(histogram)
# print(cumulative_distribution)
#
# # 假设我们认为如果超过 95% 的像素分布在最亮的 5% 的范围内，则图像过度曝光
# overexposure_threshold = 0.95
# is_overexposed = np.any(cumulative_distribution[-int(0.05 * len(cumulative_distribution))] > overexposure_threshold)
#
# print(f"The image is {'--- overexposed' if is_overexposed else '+++ not overexposed'} ")
