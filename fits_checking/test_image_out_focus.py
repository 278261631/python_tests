import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import gaussian_filter, sobel
from skimage import feature

# 替换为你的 FITS 文件路径
fits_file_path = r'E:/test_download/img_check/lines.fit'

# 使用 astropy 读取 FITS 文件
with fits.open(fits_file_path) as hdul:
    # 假设数据在第一个HDU 中
    data = hdul[0].data

# 对图像应用高斯滤波器以减少噪声
blurred = gaussian_filter(data, sigma=1)

# 使用 Sobel 算子计算图像的梯度
gradient_x = sobel(blurred, axis=0, mode='constant')
gradient_y = sobel(blurred, axis=1, mode='constant')

# 计算梯度的幅度
gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)

# 计算梯度幅度的平均值作为清晰度的指标
sharpness_metric = np.mean(gradient_magnitude)

# 可视化原图和梯度幅度图
plt.figure(figsize=(14, 7))

plt.subplot(1, 2, 1)
plt.imshow(data, cmap='gray')
plt.title('原始图像')

plt.subplot(1, 2, 2)
plt.imshow(gradient_magnitude, cmap='gray')
plt.title('梯度幅度')

plt.tight_layout()
plt.show()

# 根据清晰度指标判断图像是否虚焦
# 这个阈值需要根据你的具体应用场景进行调整
sharpness_threshold = 0.1  # 这个值需要调整以适应你的数据
is_out_of_focus = sharpness_metric < sharpness_threshold

print(f"根据清晰度指标，图像 {'是虚焦的' if is_out_of_focus else '是聚焦的'}。")
