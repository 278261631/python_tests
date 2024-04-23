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
solve_file_path_root = r'E:/test_download/validate/'
temp_download_path_root = r'E:/test_download/'
# 清空目录里的文件
if os.path.exists(solve_file_path_root):
    entries = os.listdir(solve_file_path_root)
    for entry in entries:
        full_path = os.path.join(solve_file_path_root, entry)
        if os.path.isfile(full_path) or os.path.islink(full_path):
            # os.remove(full_path)
            print(f'- remove  {full_path}')

cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 101  order by  id desc  limit 3000
''')
result = cursor.fetchall()
for idx, s_item in enumerate(result):
    parsed_url = urlparse(s_item[1])
    file_name = "{}.fits".format(s_item[0])
    download_file_path = os.path.join(temp_download_path_root, file_name)
    solve_file_path = os.path.join(solve_file_path_root, file_name)
    # 拷贝文件
    shutil.copy(download_file_path, solve_file_path)
    print(f'{idx} / {len(result)}')

    with fits.open(solve_file_path) as hdul:
        data = hdul[0].data  # 假设数据在第一个HDU中

    # 计算直方图
    histogram, bin_edges = np.histogram(data, bins=256, range=(data.min(), data.max()))

    # 找到直方图中的最大值和对应的索引
    peak_value = np.max(histogram)
    peak_position = np.argmax(histogram)

    # 计算峰值对应的灰度级
    # 直方图的索引对应于左边缘，因此峰值位于左边缘和右边缘之间
    peak_graylevel = (bin_edges[peak_position] + bin_edges[peak_position + 1]) / 2

    over_exp = False
    # 输出峰值位置和对应的灰度级
    print(f"{peak_position}Peak Value: {peak_value}  gray {peak_graylevel}       idx {idx}   {s_item[0]}")
    if peak_graylevel < 10:
        over_exp = True
        print(f"!!!1-> {peak_position}Peak Value: {peak_value}  gray {peak_graylevel}       idx {idx}   {s_item[0]}")
    if peak_position < 40:
        print(f"!!!2-> {peak_position}Peak Value: {peak_value}  gray {peak_graylevel}       idx {idx}   {s_item[0]}")
    if peak_graylevel > 60000:
        over_exp = True
        print(f"!!!3-> {peak_position}Peak Value: {peak_value}  gray {peak_graylevel}       idx {idx}   {s_item[0]}")
    if peak_position > 240:
        over_exp = True
        print(f"!!!4-> {peak_position}Peak Value: {peak_value}  gray {peak_graylevel}       idx {idx}   {s_item[0]}")

    if over_exp:
        sql_str = f'UPDATE image_info SET status=111 WHERE id = {s_item[0]}'
        print(sql_str)
        cursor.execute(sql_str)
        conn.commit()
    # 删除文件
    os.remove(solve_file_path)


# 解析fits wcs

# 加载wcs 更新数据库

# 关闭游标和连接
cursor.close()
conn.close()

