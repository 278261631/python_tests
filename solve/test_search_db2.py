import os
import subprocess
from urllib.parse import urlparse

import numpy as np
from astropy.coordinates import SkyCoord

from solve.scan_by_days import scan_by_days
import sqlite3
from astropy import units as u

# select center_a_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.a_v_x) +(0.9391063563145884*image_info.a_v_y)+(0.2893441353837993*image_info.a_v_z) ))))) as ta,
#        center_b_theta, abs(90-(degrees(acos(((-0.18536240948083066*image_info.b_v_x) +(0.9391063563145884*image_info.b_v_y)+(0.2893441353837993*image_info.b_v_z) ))))) as tb
# from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb
#
# -- [-0.7340666984702854, 0.25515079385691664, 0.6293203910498374]
# select center_a_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.a_v_x) +(0.25515079385691664*image_info.a_v_y)+(0.6293203910498374*image_info.a_v_z) ))))) as ta,
#        center_b_theta, abs(90-(degrees(acos(((-0.7340666984702854*image_info.b_v_x) +(0.25515079385691664*image_info.b_v_y)+(0.6293203910498374*image_info.b_v_z) ))))) as tb,
#        *
# from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb order by  ta

# 10.72340	+39.0
Ha = 15.34043
dec = +0.0
target_ra_deg = Ha*15
target_dec_deg = dec

target_coord = SkyCoord(ra=target_ra_deg, dec=target_dec_deg, unit='deg')
target_coord_cartesian = target_coord.cartesian
target_vector = [target_coord_cartesian.x.value, target_coord_cartesian.y.value, target_coord_cartesian.z.value]
print(target_vector)
a = [0.05095289251243462, -0.9081693071948632, 0.41549044780093114]
b = [0.02261708531972795, 0.02261708531972795, 0.02261708531972795]
c = [0.05191675, -0.91609274, 0.39759118]

dot_product_a = target_vector[0]*a[0] + target_vector[1]*a[1] + target_vector[2]*a[2]
dot_product_b = target_vector[0]*b[0] + target_vector[1]*b[1] + target_vector[2]*b[2]
dot_product_c = target_vector[0]*c[0] + target_vector[1]*c[1] + target_vector[2]*c[2]

magnitude_target = target_vector[0]**2 + target_vector[1]**2 + target_vector[2]**2
magnitude_target = magnitude_target**0.5
magnitude_a = a[0]**2 + a[1]**2 + a[2]**2
magnitude_a = magnitude_a**0.5
magnitude_b = b[0]**2 + b[1]**2 + b[2]**2
magnitude_b = magnitude_b**0.5
magnitude_c = c[0]**2 + c[1]**2 + c[2]**2
magnitude_c = magnitude_c**0.5
print(magnitude_target)
print(magnitude_a)
print(magnitude_b)
print(f'mag c  {magnitude_c}')
cos_theta_a = dot_product_a / (magnitude_target * magnitude_a)
cos_theta_b = dot_product_b / (magnitude_target * magnitude_b)
cos_theta_c = dot_product_c / (magnitude_target * magnitude_c)

# select acos(数值) from
# SELECT degrees(acos(cos_value)) FROM 您的表名
angle_rad_a = np.arccos(cos_theta_a)
angle_deg_from_rad_a = np.degrees(angle_rad_a)
angle_rad_b = np.arccos(cos_theta_b)
angle_deg_from_rad_b = np.degrees(angle_rad_b)
angle_rad_c = np.arccos(cos_theta_c)
angle_deg_from_rad_c = np.degrees(angle_rad_c)


target_t_a = abs(90 - angle_deg_from_rad_a)
target_t_b = abs(90 - angle_deg_from_rad_b)
target_t_c = abs(90 - angle_deg_from_rad_c)

print(target_t_a)
print(target_t_b)
print(f't to c {target_t_c}    deg    {angle_deg_from_rad_c}   rad {angle_rad_c}')


c_coord = SkyCoord(ra=273.2435933286, dec=23.42767765074, unit='deg')
c_coord_cartesian = c_coord.cartesian
print(f'c xyz  {c_coord_cartesian}')

offset = target_coord.spherical_offsets_to(c_coord)
# offset = target_coord.di(c_coord)
print(f'---  {offset}')



conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()
sql_str = f'select id, center_a_theta, abs(90-(degrees(acos((({target_vector[0]}*image_info.a_n_x) +({target_vector[1]}*image_info.a_n_y)+({target_vector[2]}*image_info.a_n_z) ))))) as ta, center_b_theta, abs(90-(degrees(acos((({target_vector[0]}*image_info.b_n_x) +({target_vector[1]}*image_info.b_n_y)+({target_vector[2]}*image_info.b_n_z) ))))) as tb, *  from  image_info where status=100 and ta not null and  center_a_theta>ta and center_b_theta>tb order by  ta '
sql_str = f'-- select id, center_a_theta from  image_info where status=100 '
# cursor.execute('''
#     SELECT id,wcs_info FROM image_info WHERE status = 100 and id = 2266  limit 1
cursor.execute(sql_str)
result = cursor.fetchall()
print(f'len : {len(result)}')
for idx, s_item in enumerate(result):
    header_string = s_item[1]
    print(f'{idx}')

