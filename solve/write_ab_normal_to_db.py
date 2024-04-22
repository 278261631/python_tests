import sqlite3

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import wcs
import numpy as np
from numpy.linalg import inv

from solve.download_solve_pipline_astap import plane_normal_vector

# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()
# cursor.execute('''
#     SELECT id,center_v_x,center_v_y,center_v_z, a_v_x,a_v_y,a_v_z,b_v_x,b_v_y,b_v_z FROM image_info WHERE status = 100 and id = 2266  limit 1
cursor.execute('''
    SELECT id,center_v_x,center_v_y,center_v_z, a_v_x,a_v_y,a_v_z,b_v_x,b_v_y,b_v_z FROM image_info WHERE status = 100 
''')
result = cursor.fetchall()
o_center = [0, 0, 0]
for idx, s_item in enumerate(result):
    img_center = [s_item[1], s_item[2], s_item[3]]
    img_a_center = [s_item[4], s_item[5], s_item[6]]
    img_b_center = [s_item[7], s_item[8], s_item[9]]
    plane_normal_vector_a = plane_normal_vector(o_center, img_center, img_a_center)
    plane_normal_vector_b = plane_normal_vector(o_center, img_center, img_b_center)
    print(f' {idx}  ')

    print(f'C {s_item[1]} {s_item[2]} {s_item[3]} ')
    print(f'a {s_item[4]} {s_item[5]} {s_item[6]} ')
    print(f'b {s_item[7]} {s_item[8]} {s_item[9]} ')
    print(f' {plane_normal_vector_a}   {plane_normal_vector_b}  ')

    sql_str = f'UPDATE image_info SET a_n_x={plane_normal_vector_a[0]},a_n_y={plane_normal_vector_a[1]},a_n_z={plane_normal_vector_a[2]},b_n_x={plane_normal_vector_b[0]},b_n_y={plane_normal_vector_b[1]},b_n_z={plane_normal_vector_b[2]} WHERE id = {s_item[0]}'
    print(sql_str)
    cursor.execute(sql_str)

conn.commit()
cursor.close()
conn.close()
