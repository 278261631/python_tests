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
    SELECT id, file_path FROM image_info WHERE status = 0   limit 100
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

# 创建一个锁
mp_lock = multiprocessing.Lock()
# 最大线程数
max_process = 3


def worker_download_fits(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程
        file_name = "{}.fits".format(d_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        print(f'[{d_item[0]}]:{file_name}       {p_name} / {len(db_search_result)}')

        with subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", d_item[1]],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) \
                as proc_down:
            print("the commandline is {}".format(proc_down.args))
            proc_down.communicate()

        with mp_lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            sql_str = f'UPDATE image_info SET status=1 ' \
                      f'WHERE id = {d_item[0]}'
            cursor.execute(sql_str)
            print(f'{sql_str}')
            print(f'{db_path}')
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Process {p_name} has finished processing data: ")
            r_queue.put(p_name)  # 将结果放回结果队列


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

    # 打印结果
    while not results_queue.empty():
        print(f"Result: {results_queue.get()}")

    print("All tasks have been completed.")


