import sqlite3

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import wcs
import numpy as np
from numpy.linalg import inv


def calculate_pixel_position(ra, dec, wcs_info_p):
    CRVAL1 = wcs_info_p.wcs.crval[0]
    CRVAL2 = wcs_info_p.wcs.crval[1]
    CRPIX1 = wcs_info_p.wcs.crpix[0]
    CRPIX2 = wcs_info_p.wcs.crpix[1]
    CD = np.array([[wcs_info_p.wcs.cd[0][0], wcs_info_p.wcs.cd[0][1]],
                   [wcs_info_p.wcs.cd[1][0], wcs_info_p.wcs.cd[1][1]]])

    # 将RA, DEC转换为弧度
    ra_rad = np.radians(ra)
    dec_rad = np.radians(dec)

    # 计算ΔRA和ΔDEC
    delta_RA = (ra - CRVAL1) * np.cos(dec_rad)
    delta_DEC = dec - CRVAL2

    # 计算像素坐标
    delta = np.array([delta_RA, delta_DEC])
    pix_coords = inv(CD).dot(delta) + np.array([CRPIX1, CRPIX2])

    return pix_coords


def wcs_world2pix_raw(ra, dec, crval1, crval2, crpix1, crpix2, cd11, cd12, cd21, cd22):
    print(f'{ra-crval1}* {cd11}    {dec-crval2} * {cd12}')
    print(f'{ra-crval1}* {cd21}    {dec-crval2} * {cd22}')
    x = cd11 * (ra - crval1) + cd12 * (dec - crval2) + crpix1
    y = cd21 * (ra - crval1) + cd22 * (dec - crval2) + crpix2
    return x, y


header_string = ''
print(f'1.  {header_string}')
# # 打开 FITS 文件
# with fits.open(r'E:\testimg\input_1\GY1_K040-6_No Filter_60S_Bin2_UTC20231010_200646_-19.9C_.fit') as hdulist:
#     # 获取 WCS 信息
#     wcs_info = wcs.WCS(hdulist[0].header)
#     header_string = wcs_info.to_header_string()

# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()
# cursor.execute('''
#     SELECT id, wcs_info FROM image_info WHERE status = 100 and id = 2266  limit 1
cursor.execute('''
    SELECT id, wcs_info FROM image_info WHERE status = 100 and id = 3829  limit 1
''')
result = cursor.fetchall()
for idx, s_item in enumerate(result):
    header_string = s_item[1]
    print(f' {idx}   {s_item[0]}  {s_item[1]}')

print(f'2.  {header_string}')
wcs_info = wcs.WCS(header_string)
print('-----------------')
print(wcs_info.wcs.crval)
print(wcs_info.wcs.crpix)
# print(wcs_info.wcs.cd)
print('-----------------')

ra_1, dec_1 = wcs_info.wcs_pix2world(0, 0, 1)
ra_2, dec_2 = wcs_info.wcs_pix2world(4799, 0, 1)
ra_3, dec_3 = wcs_info.wcs_pix2world(4799, 3210, 1)
ra_4, dec_4 = wcs_info.wcs_pix2world(3210, 0, 1)
ra_a, dec_a = wcs_info.wcs_pix2world(2400, 0, 1)
ra_b, dec_b = wcs_info.wcs_pix2world(0, 1605, 1)
a_coord = SkyCoord(ra=ra_a, dec=dec_a, unit='deg')
a_coord_cartesian = a_coord.cartesian
b_coord = SkyCoord(ra=ra_b, dec=dec_b, unit='deg')
b_coord_cartesian = b_coord.cartesian
print(f'{ra_1}   {dec_1}')
print(f'{ra_2}   {dec_2}')
print(f'{ra_3}   {dec_3}')
print(f'{ra_4}   {dec_4}')
print(f'a:   {ra_a}   {dec_a}     {a_coord_cartesian} ')
print(f'b:   {ra_b}   {dec_b}     {b_coord_cartesian} ')

x1, y1 = wcs_info.wcs_world2pix(ra_1, dec_1, 1)
x2, y2 = wcs_info.wcs_world2pix(ra_2, dec_2, 1)
x3, y3 = wcs_info.wcs_world2pix(ra_3, dec_3, 1)
x4, y4 = wcs_info.wcs_world2pix(ra_4, dec_4, 1)
xt, yt = wcs_info.wcs_world2pix(160.8333, 39, 1)

print(f'{x1}   {y1}')
print(f'{x2}   {y2}')
print(f'{x3}   {y3}')
print(f'{x4}   {y4}')
print(f't    {xt}   {yt}')

# sql_x, sql_y = wcs_world2pix_raw(ra_1, dec_1, wcs_info.wcs.crval[0], wcs_info.wcs.crval[1], wcs_info.wcs.crpix[0],
#                                  wcs_info.wcs.crpix[1], wcs_info.wcs.cd[0][0], wcs_info.wcs.cd[0][1],
#                                  wcs_info.wcs.cd[1][0], wcs_info.wcs.cd[1][1])
# print(f'------- {sql_x} {sql_y} -----------')
# sql_x, sql_y = wcs_world2pix_raw(ra_2, dec_2, wcs_info.wcs.crval[0], wcs_info.wcs.crval[1], wcs_info.wcs.crpix[0],
#                                  wcs_info.wcs.crpix[1], wcs_info.wcs.cd[0][0], wcs_info.wcs.cd[0][1],
#                                  wcs_info.wcs.cd[1][0], wcs_info.wcs.cd[1][1])
# print(f'------- {sql_x} {sql_y} -----------')
# sql_x, sql_y = wcs_world2pix_raw(ra_3, dec_3, wcs_info.wcs.crval[0], wcs_info.wcs.crval[1], wcs_info.wcs.crpix[0],
#                                  wcs_info.wcs.crpix[1], wcs_info.wcs.cd[0][0], wcs_info.wcs.cd[0][1],
#                                  wcs_info.wcs.cd[1][0], wcs_info.wcs.cd[1][1])
# print(f'------- {sql_x} {sql_y} -----------')
# sql_x, sql_y = wcs_world2pix_raw(ra_4, dec_4, wcs_info.wcs.crval[0], wcs_info.wcs.crval[1], wcs_info.wcs.crpix[0],
#                                  wcs_info.wcs.crpix[1], wcs_info.wcs.cd[0][0], wcs_info.wcs.cd[0][1],
#                                  wcs_info.wcs.cd[1][0], wcs_info.wcs.cd[1][1])
# cord = calculate_pixel_position(ra_4, dec_4, wcs_info)
# print(f'------- {cord}  -----------')
