import sqlite3

from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import wcs
import numpy as np
from numpy.linalg import inv

from solve.download_solve_pipline_astap import plane_normal_vector


height = 3211
# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()
# cursor.execute('''
#     SELECT id,wcs_info FROM image_info WHERE status = 100 and id = 2266  limit 1
cursor.execute('''
    SELECT id,wcs_info FROM image_info WHERE status = 100  
''')
result = cursor.fetchall()
o_center = [0, 0, 0]
for idx, s_item in enumerate(result):
    header_string = s_item[1]
    wcs_info = wcs.WCS(header_string)
    ra_mid_y, dec_mid_y = wcs_info.wcs_pix2world(0, (height + 1) / 2, 1)
    coord_mid_y = SkyCoord(ra=ra_mid_y, dec=dec_mid_y, unit='deg')
    cartesian_mid_y = coord_mid_y.cartesian
    print(f' {idx}   {s_item[0]}      =     {cartesian_mid_y.x}, {cartesian_mid_y.y}, {cartesian_mid_y.z}')

    sql_str = f'UPDATE image_info SET b_v_x={cartesian_mid_y.x},b_v_y={cartesian_mid_y.y},b_v_z={cartesian_mid_y.z} WHERE id = {s_item[0]}'
    print(sql_str)
    cursor.execute(sql_str)

conn.commit()
cursor.close()
conn.close()
