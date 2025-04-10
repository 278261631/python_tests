import matplotlib
import numpy as np
from astropy.io import fits
from astropy.io.fits import HDUList, PrimaryHDU, BinTableHDU
from astropy.wcs import WCS
from astropy import units as u
from astropy.table import vstack
from astropy.table import Table

matplotlib.use('Agg')  # 在导入pyplot之前设置非交互式后端
import matplotlib.pyplot as plt

# 读取FITS文件
# filename = 'GY1_K035-4_C_60S_Bin2_UTC20240623_193150_-13.1C__pp.diff1.fits'
# target_coord = "20 13 46.63 +36 24 12.4"

# filename = 'GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
# target_coord = "12 17 10.91 +54 36 11.8"

# filename = 'zogy_GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
# target_coord = "12 17 10.91 +54 36 11.8"
filename = 'hotp_GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
target_coord = "12 17 10.91 +54 36 11.8"

x_coords = np.array([])
y_coords = np.array([])
mag_data = np.array([])
dmag_data = np.array([])

# 读取FITS文件时获取WCS信息
with fits.open(filename) as hdul:
    data = hdul[0].data
    wcs = WCS(hdul[0].header)  # 获取WCS坐标系

# 添加目标坐标转换（在cat_data处理后添加）
ra_hms, dec_dms = target_coord.split()[:3], target_coord.split()[3:]
from astropy.coordinates import SkyCoord

# 将字符串坐标转换为SkyCoord对象
c = SkyCoord(' '.join(ra_hms), ' '.join(dec_dms),
            unit=(u.hourangle, u.deg))
# 转换为像素坐标
target_x, target_y = wcs.world_to_pixel(c)


cat_filename = filename.replace('.diff1.fits', '.diff1.fixedsrc.cat')
with open(cat_filename, 'r') as f:
    line_count = sum(1 for line in f if not line.startswith('#'))
if line_count > 1:
    cat_data = np.loadtxt(cat_filename, delimiter=',', skiprows=1, comments=None, usecols=[6,7,8,9],)
    cat_data = cat_data[cat_data[:, 2].argsort()[::-1]]

    # 在现有过滤条件后添加空间过滤
    distance_mask = (
        (cat_data[:, 0] - target_x)**2 +
        (cat_data[:, 1] - target_y)**2
    ) <= 400**2  # 使用平方比较避免开根号运算

    filtered_mask = cat_data[:, 3] < 0.9

    # cat_data = cat_data[filtered_mask]
    cat_data = cat_data[distance_mask]

    # 合并掩码（同时满足显著性和距离条件）
    # combined_mask = filtered_mask & distance_mask
    # cat_data = cat_data[combined_mask]

    mag_data = cat_data[:, 2]
    dmag_data = cat_data[:, 3]
    x_coords = cat_data[:, 0]
    y_coords = cat_data[:, 1]
    # 快速验证坐标系的临时代码
    print("First 10 coordinates:")
    for i in range(10):
        print(f"mag [{mag_data[i]:.5f}] [{dmag_data[i]:.5f}]  ({x_coords[i]:.1f}, {y_coords[i]:.1f})")



# 在图像数据层直接绘制标记（修改像素值）
marked_data = data.copy()

radius = 15  # 圆圈半径
y_indices, x_indices = np.indices(data.shape)
for x, y in zip(x_coords.astype(int), y_coords.astype(int)):
    # 创建圆形掩模
    circle_mask = ((x_indices - x)**2 + (y_indices - y)**2 <= radius**2) & \
                  ((x_indices - x)**2 + (y_indices - y)**2 >= (radius-0.5)**2)
    marked_data[circle_mask] = np.max(data)  # 仅绘制圆形轮廓

radius = 25
circle_mask = ((x_indices - target_x)**2 + (y_indices - target_y)**2 <= radius**2) & \
              ((x_indices - target_x)**2 + (y_indices - target_y)**2 >= (radius-0.5)**2)
marked_data[circle_mask] = np.max(data)  # 仅绘制圆形轮廓

# 保存修改后的数据
fits.writeto('hotp_marked_image.fits', marked_data, header=fits.getheader(filename), overwrite=True)

