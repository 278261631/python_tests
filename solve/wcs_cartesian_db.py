import math

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import wcs
import astropy.units as u
import numpy as np
from numpy.linalg import inv


# 打开 FITS 文件
# hdul = fits.open(r"E:/testimg/tycho/GY1_K008-5_No Filter_60S_Bin2_UTC20231218_141114_-25C_.fit")
hdul = fits.open(r"E:/testimg/tycho/GY1_K040-6_No Filter_60S_Bin2_UTC20231010_200646_-19.9C_.fit")
# hdul = fits.open(r'E:\testimg\tycho\12_7deg.fits')
# 获取 WCS 信息
wcs_info = wcs.WCS(hdul[0].header, naxis=2)

# 打印 WCS 信息
print(wcs_info)
header_string = wcs_info.to_header_string()
print(header_string)
# wcs_info_load = wcs.WCS(header_string)
print('-----------------')
print(wcs_info.wcs.crval)
print(wcs_info.wcs.crpix)
print(wcs_info.wcs.cd)
print('-----------------')
# 获取总宽高
image_data = hdul[0].data
# 获取图像的宽度和高度
width, height = image_data.shape[1], image_data.shape[0]
print(f'x: {width}  y:{height}    x/2 {(width+1)/2}   y/2 {(height+1)/2}')
# 获取x y中点
ra_mid_x, dec_mid_x = wcs_info.wcs_pix2world((width+1)/2, 0, 1)
ra_mid_y, dec_mid_y = wcs_info.wcs_pix2world(0, (height+1)/2, 1)
#  tycho 的识别结果有时候不是以图像中心点为 crpix ,会有少量偏移?
ra_mid_img, dec_mid_img = wcs_info.wcs_pix2world((width+1)/2, (height+1)/2, 1)
ra_corner_img, dec_corner_img = wcs_info.wcs_pix2world(0, 0, 1)
print(f'x_mid: {ra_mid_x}  {dec_mid_x}    y_mid: {ra_mid_y}  {dec_mid_y}   img_mid: {ra_mid_img}  {dec_mid_img}  ')

# 存储 wcs
# 存储 四角坐标极大 极小值，用于初步筛选数据？极轴？？？
# 改成存储图像中心向量  然后计算 目标向量和中心向量夹角？？

# 获取x y 中点 图像中心点image_c test_target cartesian坐标
coord_img_center = SkyCoord(ra=ra_mid_img, dec=dec_mid_img, unit='deg')
cartesian_img_center = coord_img_center.cartesian
coord_img_corner = SkyCoord(ra=ra_corner_img, dec=dec_corner_img, unit='deg')
cartesian_img_corner = coord_img_corner.cartesian

print(f'center {cartesian_img_center}   ')

# 计算两个点之间的角距离（以弧度为单位）
angle_deg = coord_img_center.separation(coord_img_corner)

# 输出结果
print(f"两个点之间的夹角（度）: {angle_deg} 度")

u_x, u_y, u_z = coord_img_center.cartesian.x, coord_img_center.cartesian.y, coord_img_center.cartesian.z
v_x, v_y, v_z = coord_img_corner.cartesian.x, coord_img_corner.cartesian.y, coord_img_corner.cartesian.z

# 计算点积
dot_product = u_x * v_x + u_y * v_y + u_z * v_z

# 计算余弦值
cos_theta = dot_product

# 计算夹角的弧度值
theta = math.acos(cos_theta)

# 如果需要，将弧度转换为度数
theta_degrees = math.degrees(theta)

# 输出结果
print(f"两个单位向量之间的夹角（弧度）: {theta}")
print(f"两个单位向量之间的夹角（度）: {theta_degrees} 度")



