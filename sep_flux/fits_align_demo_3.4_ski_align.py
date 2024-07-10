import os

import matplotlib
import numpy as np
import sep
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from astropy.wcs import WCS
import matplotlib.pyplot as plt
from reproject import reproject_interp
matplotlib.use('TkAgg')
from skimage import data
from skimage.feature import ORB, match_descriptors, match_template
from skimage.transform import SimilarityTransform, warp
from skimage.transform import estimate_transform
# hdu1 = fits.open(get_pkg_data_filename('src_process/test_/109120220506194824.fits'))[0]
# hdu2 = fits.open(get_pkg_data_filename('src_process/test_/209120220407205125.fits'))[0]


# 读取FITS文件
hdu1 = fits.open('src_process/test_/109120220506194824.fits')
# hdu1 = fits.open('src_process/test_/109120220407205235.fits')
hdu2 = fits.open('src_process/test_/209120220407205125.fits')
image_a = hdu1[0].data
image_b = hdu2[0].data

# # 星点检测，这里使用 ORB 作为示例
# orb = ORB(n_keypoints=100)
# keypoints_a = orb.detect(image_a)
# keypoints_b = orb.detect(image_b)

image_a = image_a.astype(np.float32)
image_b = image_b.astype(np.float32)

bkg_a = sep.Background(image_a)
bkg_a_image = bkg_a.back()
data_a_no_bg = image_a - bkg_a_image

bkg_b = sep.Background(image_b)
bkg_b_image = bkg_b.back()
data_b_no_bg = image_b - bkg_b_image

data_a = sep.extract(image_a, 516, err=bkg_a.globalrms)
data_b = sep.extract(image_b, 516, err=bkg_b.globalrms)

# 假设 sep.extract 返回的数据中 x 和 y 坐标分别是 data['x'] 和 data['y']
# 将星点坐标转换为 numpy 数组
x_a, y_a = data_a['x'], data_a['y']
x_b, y_b = data_b['x'], data_b['y']
points1 = np.column_stack([x_a, y_a])
points2 = np.column_stack([x_b, y_b])

min_points = min(points1.shape[0], points2.shape[0])
points1 = points1[:min_points]
points2 = points2[:min_points]


# 使用 estimate_similar_transform 进行多边形匹配
transform = estimate_transform('polynomial', points1, points2)

# 应用变换到第一个图像的坐标上
points1_transformed = transform(points1)

# 可视化原始和变换后的坐标
plt.figure(figsize=(10, 5))

# 绘制第二个图像的星点
plt.subplot(1, 2, 1)
plt.imshow(image_b, origin='lower', cmap='gray')
plt.scatter(points2[:, 0], points2[:, 1], color='red', label='Original Points in Image B')

# 绘制变换后第一个图像的星点
plt.subplot(1, 2, 2)
plt.imshow(image_a, origin='lower', cmap='gray')
plt.scatter(points1_transformed[:, 0], points1_transformed[:, 1], color='red', label='Transformed Points in Image A')
plt.legend()

plt.tight_layout()
plt.show()




# hdu_a_aligned = fits.PrimaryHDU(image_a_aligned)
# hdu_a_aligned.header = fits.open('file_a.fits')[0].header.copy()
# hdu_a_aligned.writeto('src_process/test_/ski_align.fits', overwrite=True)




