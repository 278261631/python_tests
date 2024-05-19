import datetime
import multiprocessing
import os
from math import sqrt
import numpy as np
import sep
from astropy.io import fits
from skimage.exposure import histogram

from solve import config_manager
import sqlite3
import concurrent.futures
import subprocess

# 连接到SQLite数据库
db_path = config_manager.ini_config.get('database', 'path')
temp_download_path = config_manager.ini_config.get('download', 'temp_download_path')

conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
cursor_search.execute('''
    SELECT id, file_path FROM image_info WHERE status = 0   limit 30
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

if __name__ == '__main__':

    for index, search_item in enumerate(db_search_result):
        file_name = "{}.fits".format(search_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        print(f'[{search_item[0]}]:{file_name}        / {len(db_search_result)}')
        download_code = 0
        proc_down = subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", search_item[1]],
                                     stdout=None, stderr=None)
        print("the commandline is {}".format(proc_down.args))
