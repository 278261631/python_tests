import datetime
import multiprocessing
import os
import shutil
from math import sqrt
import numpy as np
import sep
from astropy.io import fits
from skimage.exposure import histogram

from solve import config_manager
import sqlite3
import concurrent.futures
import subprocess

from tools.fits_check import copy_or_download
from tools.regex_from_string import get_yyyy_from_path

# 连接到SQLite数据库
db_path = 'fits_wcs_2020_2024.db'
temp_download_path = 'e:/fix_data/'
file_in_disk_path_root = 'e:/'

conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
sql_search = f'select id,file_path from  image_info where wcs_info is null and chk_result=1 and blob_dog_num>500 and status=111'
cursor_search.execute(sql_search)
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

# 创建一个锁
mp_lock = multiprocessing.Lock()
# 最大线程数
max_process = 4


def worker_download_fits(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程
        file_name = "{}.fits".format(d_item[0])
        file_name_txt_ok = "{}_ok.txt".format(d_item[0])
        yyyy = get_yyyy_from_path(d_item[1])
        save_file_path = os.path.join(temp_download_path, yyyy, file_name)
        save_file_path_ok = os.path.join(temp_download_path, yyyy, file_name_txt_ok)

        file_in_disk_dir = os.path.join(temp_download_path, yyyy)
        # print(f'?{file_in_disk_dir}')
        if not os.path.exists(file_in_disk_dir):
            print(f'+{file_in_disk_dir}')
            os.makedirs(file_in_disk_dir, exist_ok=True)
        file_in_disk_path = os.path.join(file_in_disk_path_root, yyyy, file_name)
        print(f'[{d_item[0]}]:{file_name}       {p_name} {r_queue.qsize()} / {len(db_search_result)}')
        download_code = 0
        r_queue.put(d_item[0])
        success = copy_or_download(save_file_path, d_item[1], file_in_disk_path)
        if success:
            with open(save_file_path_ok, 'w', encoding='utf-8') as file:
                file.write(f'{d_item[0]},ok')


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()
    for search_item in db_search_result:
        data_queue.put(search_item)
    processes = []

    # 启动进程
    for i in range(max_process):
        name = f"p_{i+1}"
        proc = multiprocessing.Process(target=worker_download_fits, args=(data_queue, results_queue, name))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

    print(f'r_size {results_queue.qsize()}')

    print("All tasks have been completed.")


