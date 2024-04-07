import math

from astropy.io import fits
from astropy import wcs


def my_all_world2pix(wcs_info, world_coords):
    """
  简化的世界坐标到像素坐标转换函数
  """
    # 解析 WCS 信息 (示例，需要根据实际情况进行修改)
    ctype = wcs_info['CTYPE']
    crval = wcs_info['CRVAL']
    cd = wcs_info['CD']

    # 计算中间坐标系坐标
    intermediate_coords = world_coords - crval

    # 应用线性变换矩阵
    pixel_coords = cd @ intermediate_coords

    # 返回像素坐标
    return pixel_coords


def my_all_world2pix_fix(wcs_info, world_coords):
    """
  简化的世界坐标到像素坐标转换函数
  """
    # 解析 WCS 信息 (示例，需要根据实际情况进行修改)
    crval = wcs_info.crval
    crpix = wcs_info.crpix
    cd = wcs_info.cd

    # 计算中间坐标系坐标
    intermediate_coords = world_coords - crval

    # 应用线性变换矩阵
    pixel_coords = cd @ intermediate_coords

    # 返回像素坐标
    return pixel_coords


hdul = fits.open(r"E:/testimg/tycho/GY1_K008-5_No Filter_60S_Bin2_UTC20231218_141114_-25C_.fit")
header = hdul[0].header

w = wcs.WCS(header)
print(f'{w}')
print(f'{w.wcs.crval}')
print(f'{w.wcs.crpix}')
print(f'{w.wcs.cd}')
# ctype = w.wcs.ctype

# 将像素坐标转换为世界坐标
pixel_coords = [[100, 100]]
world_coords = w.wcs_pix2world(pixel_coords, 1)  # 1 表示从 1 开始计数

print(f' 100,100:   {world_coords}')

pixel_coords = [[0, 0]]
world_coords = w.wcs_pix2world(pixel_coords, 1)  # 1 表示从 1 开始计数
print(f' 0  0:   {world_coords}')
pixel_coords = [[0, 4800]]
world_coords = w.wcs_pix2world(pixel_coords, 1)  # 1 表示从 1 开始计数
print(f' 0  4800:   {world_coords}')
pixel_coords = [[3211, 0]]
world_coords = w.wcs_pix2world(pixel_coords, 1)  # 1 表示从 1 开始计数
print(f' 3211  0:   {world_coords}')


# ra = 19.2739142484
# dec = 54.553772853
ra = 16.38121711
dec = 55.52591493
# ra = 15.38121711
# dec = 50.52591493
test_coords = [ra, dec]
wcs_info = hdul[0].header

# 使用 my_all_world2pix 函数进行转换
# pixel_coords = my_all_world2pix(wcs_info, test_coords)
pixel_coords = my_all_world2pix_fix(w.wcs, test_coords)

# 打印结果
print(f"像素坐标: x={pixel_coords[0]:.2f}, y={pixel_coords[1]:.2f}")

CD1_1 = w.wcs.cd[0][0]
CD1_2 = w.wcs.cd[0][1]
CD2_1 = w.wcs.cd[1][0]
CD2_2 = w.wcs.cd[1][1]
CRVAL1 = w.wcs.crval[0]
CRVAL2 = w.wcs.crval[1]
CRPIX1 = w.wcs.crpix[0]
CRPIX2 = w.wcs.crpix[1]

# x = CD1_1 * (ra - CRVAL1) * math.cos(math.radians(dec)) + CD1_2 * (dec - CRVAL2) + CRPIX1
# y = CD2_1 * (ra - CRVAL1) * math.cos(math.radians(dec)) + CD2_2 * (dec - CRVAL2) + CRPIX2
x = ((ra - CRVAL1)/CD1_1 * math.cos(math.radians(dec))) + CD1_2 * (dec - CRVAL2) + CRPIX1
y = (((ra - CRVAL1)*CD2_1) * math.cos(math.radians(dec))) + (dec - CRVAL2)/CD2_2 + CRPIX2

print(f' 100???    {x}  {y}')

X1 = (ra - CRVAL1)/CD1_1 + (dec - CRVAL2)*CD1_2
Y1 = (ra - CRVAL1)*CD2_1 + (dec - CRVAL2)/CD2_2

print(f' 100???    {X1}  {Y1}')
