import os
import subprocess
from urllib.parse import urlparse

import numpy as np
from astropy.coordinates import SkyCoord

from solve.scan_by_days import scan_by_days
import sqlite3

# 10.72340	+39.0
target_ra_deg = 160.8333
target_dec_deg = 39
# [-0.7340666984702854, 0.25515079385691664, 0.6293203910498374]
# 6:44:39.747 +16:49:7.30
# 101.1656125  16.818694444444443
# target_ra_deg = 101.1656125
# target_dec_deg = 16.818694444444443
target_coord = SkyCoord(ra=target_ra_deg, dec=target_dec_deg, unit='deg')
target_coord_cartesian = target_coord.cartesian
target_vector = [target_coord_cartesian.x.value, target_coord_cartesian.y.value, target_coord_cartesian.z.value]
print(target_vector)
a = [0.8808329889192152, 0.42082670340386485, 0.2168827594205613]
b = [0.8966232110964429, 0.8966232110964429, 0.8966232110964429]

dot_product_a = target_vector[0]*a[0] + target_vector[1]*a[1] + target_vector[2]*a[2]
dot_product_b = target_vector[0]*b[0] + target_vector[1]*b[1] + target_vector[2]*b[2]

magnitude_target = target_vector[0]**2 + target_vector[1]**2 + target_vector[2]**2
magnitude_target = magnitude_target**0.5
magnitude_a = a[0]**2 + a[1]**2 + a[2]**2
magnitude_a = magnitude_a**0.5
magnitude_b = b[0]**2 + b[1]**2 + b[2]**2
magnitude_b = magnitude_b**0.5
print(magnitude_target)
print(magnitude_a)
print(magnitude_b)
cos_theta_a = dot_product_a / (magnitude_target * magnitude_a)
cos_theta_b = dot_product_b / (magnitude_target * magnitude_b)

# select acos(数值) from
# SELECT degrees(acos(cos_value)) FROM 您的表名
angle_rad_a = np.arccos(cos_theta_a)
angle_deg_from_rad_a = np.degrees(angle_rad_a)
angle_rad_b = np.arccos(cos_theta_b)
angle_deg_from_rad_b = np.degrees(angle_rad_b)

target_t_a = abs(90 - angle_deg_from_rad_a)
target_t_b = abs(90 - angle_deg_from_rad_b)

print(target_t_a)
print(target_t_b)

# select * from image_info where

#
# # 连接到SQLite数据库
# conn = sqlite3.connect('fits_wcs.db')
# cursor = conn.cursor()
#
#
# # 下载文件
# temp_download_path = r'E:/test_download/'
# print(f'path: {temp_download_path}')
# cursor.execute('''
#     SELECT id, file_path FROM image_info WHERE status = 0  limit 100
# ''')
# result = cursor.fetchall()
# for idx, s_item in enumerate(result):
#     parsed_url = urlparse(s_item[1])
#     # file_name = parsed_url.path.split('/')[-1].decode('utf-8')
#     file_name = "{}.fits".format(s_item[0])
#
#     print(f'{idx} / {len(result)}')
#
#
# cursor.close()
# conn.close()


# --             UPDATE image_info
# --             SET status = 100, wcs_info = '-', center_v_x=0.9022402425401407, center_v_y=0.43110644874989756, center_v_z=-0.010477336844827937, a_v_x=0.9025965671110666, a_v_y=0.43039144658071005, a_v_z=0.00909064076298617,
# --             center_a_theta=1.6765122288047962, b_v_x=0.9144476412517257, b_v_y=0.40453580358837493, b_v_z=-0.011674545998155358, center_b_theta=1.121634144504597
# --             WHERE id = 1
#
#
#
#   SELECT id, file_path FROM image_info WHERE status = 1
#
#
# -- update image_info set status=1 where status = 101
#
#  SELECT id, file_path FROM image_info WHERE status = 1  limit 1
#  SELECT * FROM image_info WHERE status = 100  limit 10
#
# -- t_v = [-0.18536240948083066, 0.9391063563145884, 0.2893441353837993]
#
# select * from image_info where center_a_theta > abs(90-degrees(acos(1))) and center_b_theta > abs(90-degrees(acos(2)))
#
# select * from image_info where
#     center_a_theta > abs(90-degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))
#     and
#     center_b_theta > abs(90-degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))
#
# select center_a_theta, acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) )) as ta from  image_info where center_b_theta>ta
#
# select center_b_theta, acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )) as tb from  image_info where center_b_theta>tb
#
#
#
# select center_a_theta, degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))) as ta from  image_info --where center_b_theta>ta
#
# select center_b_theta, degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))) as tb from  image_info where center_b_theta>tb
#
#
# select center_a_theta, degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))) as ta from  image_info where status=100 order by ta desc --where center_b_theta>ta
#
#
# select center_a_theta, 90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) )))) as ta from  image_info where status=100 order by ta --where center_b_theta>ta
#
# select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta from  image_info where status=100 order by ta  --where center_b_theta>ta
# select center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb from  image_info where status=100 order by tb --where center_b_theta>ta
# -- null?????
# select  center_b_theta, acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )) as tb, * from  image_info where status=100 and id>82 and id < 90
# select  center_b_theta, ((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )as tb, * from  image_info where status=100 and id>82 and id < 90
# select  center_b_theta, ((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) )as tb, * from  image_info where status=100 order by tb desc
#
#
# select acos(0.9) from image_info where id >82 and id < 90
# select acos(1.1) from image_info where id >82 and id < 90
#
#
#
#
#
#


