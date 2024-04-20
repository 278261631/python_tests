import os
import shutil
import subprocess
from urllib.parse import urlparse

import numpy as np
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits

from solve.scan_by_days import scan_by_days
import sqlite3


# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()
solve_bin_path = r'E:/astap/astap.exe'
solve_file_path_root = r'E:/test_download/failed/'
temp_download_path_root = r'E:/test_download/'

# cursor.execute('''
#     SELECT id, file_path FROM image_info WHERE status = 101  and id%100 = 1 limit 100
cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 101  limit 200
''')
result = cursor.fetchall()
for idx, s_item in enumerate(result):
    parsed_url = urlparse(s_item[1])
    file_name = "{}.fits".format(s_item[0])
    file_name_wcs = "{}.wcs".format(s_item[0])
    file_name_ini = "{}.ini".format(s_item[0])
    wcs_file_path = os.path.join(solve_file_path_root, file_name_wcs)
    ini_file_path = os.path.join(solve_file_path_root, file_name_ini)
    download_file_path = os.path.join(temp_download_path_root, file_name)
    solve_file_path = os.path.join(solve_file_path_root, file_name)
    # solve_wcs_file_path = os.path.join(solve_file_path_root, )
    # 拷贝文件
    shutil.copy(download_file_path, solve_file_path)
    # process = subprocess.Popen([solve_bin_path, '-z', '4', '-f',
    #                             solve_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("the commandline is {}".format(process.args))
    # process.communicate()
    # process.wait()
    print(f'{idx} / {len(result)}')
    # 检查wget的退出状态
    # if process.returncode == 0:
    #     print("tycho was successful.")
    # else:
    #     print("tycho failed.")
    #     print("Error message:", process.stderr)
    #     continue
    # 读取文本文件并解析每一行以提取头信息

    # with fits.open(solve_file_path) as fits_hdul:
    #     hdul = fits_hdul
    #     image_data = hdul[0].data
    # # 获取图像的宽度和高度
    # width, height = image_data.shape[1], image_data.shape[0]
    # print(f'x: {width}  y:{height}    x/2 {(width + 1) / 2}   y/2 {(height + 1) / 2}')
    #

    # conn.commit()
    # 删除文件


# 解析fits wcs

# 加载wcs 更新数据库

# 关闭游标和连接
cursor.close()
conn.close()

