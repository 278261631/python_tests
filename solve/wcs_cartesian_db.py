from astropy.io import fits
from astropy import wcs
import numpy as np
from numpy.linalg import inv


# 打开 FITS 文件
hdul = fits.open(r"E:/testimg/tycho/GY1_K008-5_No Filter_60S_Bin2_UTC20231218_141114_-25C_.fit")
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
print(f'x_mid: {ra_mid_x}  {dec_mid_x}    y_mid: {ra_mid_y}  {dec_mid_y}  ')

# 存储 wcs
# 存储 四角坐标极大 极小值，用于初步筛选数据？极轴？？？
# 改成存储图像中心向量  然后计算 目标向量和中心向量夹角？？

# 获取x y 中点 图像中心点image_c test_target cartesian坐标






