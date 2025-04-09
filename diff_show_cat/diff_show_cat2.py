import matplotlib
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u


matplotlib.use('Agg')  # 在导入pyplot之前设置非交互式后端
import matplotlib.pyplot as plt

# 读取FITS文件
# filename = 'GY1_K035-4_C_60S_Bin2_UTC20240623_193150_-13.1C__pp.diff1.fits'
# target_coord = "20 13 46.63 +36 24 12.4"

# filename = 'GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
# target_coord = "12 17 10.91 +54 36 11.8"

filename = 'zogy_GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
target_coord = "12 17 10.91 +54 36 11.8"

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



with fits.open(filename) as hdul:
    data = hdul[0].data  # 获取第一个HDU的数据

cat_filename = filename.replace('.diff1.fits', '.diff1.fixedsrc.cat')

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





# 计算布局参数
image_height, image_width = data.shape
colorbar_width = 0.15  # 颜色条占画布宽度的比例
title_space = 0.08      # 标题预留空间比例
label_space = 0.06      # 坐标轴标签预留空间

# 创建画布（动态计算总尺寸）
fig = plt.figure(
    figsize=(
        (image_width*(1 + colorbar_width))/100,  # 总宽度 = 图像宽度 + 颜色条宽度
        image_height*(1 + title_space + label_space)/100  # 总高度 = 图像高度 + 标题空间 + 标签空间
    ),
    dpi=100,
    # constrained_layout=True  # 自动调整布局
)

# 主图像区域（左侧）
ax = fig.add_axes([
    0.08,  # 左边距
    label_space + title_space,  # 底边距（为标签和标题留空间）
    0.75,  # 宽度比例（留出颜色条空间）
    0.8    # 高度比例
])
ax.scatter(x_coords[:5000], y_coords[:5000],
          s=80,                # 点的大小
          facecolors='none',   # 空心圆
          edgecolors='red',    # 红色边框
          linewidths=1.5,      # 边框粗细
          zorder=10)           # 确保显示在最上层
max_index = len(x_coords)
max_index = min(5000, max_index)
for i in range(max_index):
    ax.text(x_coords[i] + 5, y_coords[i] + 5,  # 坐标偏移避免重叠
           f"{mag_data[i]:.4f}±{dmag_data[i]:.4f}",  # 格式化显示
           fontsize=6,
           color='red',
           alpha=0.8,
           ha='left',
           va='bottom',
           zorder=12)

# 绘制图像（保持1:1像素比例）
im = ax.imshow(
    data,
    cmap='gray',
    origin='lower',
    aspect='equal',
    interpolation='none',
    vmin=np.percentile(data, 1),
    vmax=np.percentile(data, 99)
)


ax.scatter([target_x], [target_y],
          s=200,                # 放大标记尺寸
          marker='o',           # 改为圆形标记
          facecolors='none',    # 空心填充
          edgecolors='yellow',  # 黄色边框
          linewidths=1.5,       # 加粗边框线
          zorder=11)            # 显示在最顶层

# 添加颜色条（右侧）
cax = fig.add_axes([
    0.85,  # 左边距（在主图右侧）
    label_space + title_space,
    0.03,  # 颜色条宽度
    0.8    # 与主图同高
])
plt.colorbar(im, cax=cax, label='Intensity')

# 设置标题和标签
ax.set_title(f'FITS Image: {filename}', pad=20)
ax.set_xlabel('X Pixel')
ax.set_ylabel('Y Pixel')

# 保存图像（保持像素精度）
# plt.savefig('diff_image2.png',
plt.savefig('zogy_diff_image2.png',
           dpi=100,
           bbox_inches='tight',
           pad_inches=0.1)
plt.close()
