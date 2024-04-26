from astropy.io import fits
from skimage.feature import shape_index
import numpy as np

fits_file_path = r'E:/test_download/img_check/lines.fit'
# 加载FITS文件
hdu_list = fits.open(fits_file_path)
data = hdu_list[0].data  # 假设数据在主HDU中

# 计算shape index
# hessian_matrix = np.gradient(data)  # 计算梯度和Hessian矩阵
S = shape_index(data)

# 根据shape index的值来识别线条和椭圆形状
# 通常，线条的形状指数接近0，椭圆的形状指数接近1
# 这里需要根据实际数据调整阈值
line_threshold = 0.01  # 线条的阈值，可能需要调整
ellipse_threshold = 0.9  # 椭圆的阈值，可能需要调整

# 创建掩码来识别线条和椭圆
line_mask = (S > -line_threshold) & (S < line_threshold)
ellipse_mask = (S > ellipse_threshold)

# 应用掩码来提取线条和椭圆的位置
lines = data[line_mask]
ellipses = data[ellipse_mask]
print(f'l:   {len(lines)}   {lines}')
print(f'e:   {len(ellipses)}   {ellipses}')
