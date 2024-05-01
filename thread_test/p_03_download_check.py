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
#  拥挤在过曝区域 %5
threshold_percentage_95 = 95
# 拥挤在低曝光 3% 的范围
threshold_percentage_10 = 3


conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
cursor_search.execute('''
    SELECT id, file_path FROM image_info WHERE status = 1 and chk_result is  null   limit 30000
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

# 创建一个锁
mp_lock = multiprocessing.Lock()
# 最大线程数
max_process = 10


def worker_check_fits(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            # print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程
        file_name = "{}.fits".format(d_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        print(f'[{d_item[0]}]:{file_name}       {p_name} {r_queue.qsize() + 1} / {len(db_search_result)}')

        with fits.open(save_file_path) as hdul:
            # 假设数据在第一个 HDU 中
            data = hdul[0].data
        hist, bin_edges = histogram(data)
        # print(f'{len(hist)}   {len(bin_edges)}')
        # 计算直方图的累积分布函数 (CDF)
        cdf = np.cumsum(hist) / np.sum(hist)
        threshold_index_95 = int(threshold_percentage_95 / 100 * len(cdf))
        threshold_index_10 = int(threshold_percentage_10 / 100 * len(cdf))
        is_overexposed = cdf[-1] - cdf[threshold_index_95] > 0.9
        is_underexposed = cdf[-1] - cdf[threshold_index_10] < 0.1
        exp_check_pass = not (is_underexposed or is_overexposed)

        image_data_float = data.astype(np.float64)
        bkg = sep.Background(image_data_float)
        data_sub = image_data_float - bkg
        try:
            objects = sep.extract(data_sub, 10, err=bkg.globalrms)
        except Exception as e:
            print(e)
            continue
        sep_obj_len = len(objects)
        all_check_pass = exp_check_pass and (sep_obj_len > 200)

        with mp_lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            sql_str = f'UPDATE image_info SET status=1,' \
                      f'chk_exp_hist={1 if exp_check_pass else -1},blob_dog_num={sep_obj_len},' \
                      f'chk_result =  {1 if all_check_pass else -1},status=1 ' \
                      f'WHERE id = {d_item[0]}'
            cursor.execute(sql_str)
            # print(f'{sql_str}')
            # print(f'{db_path}')
            conn.commit()
            cursor.close()
            conn.close()
            # print(f"Process {p_name}  [{r_queue.qsize()}]has finished processing data: ")
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
        proc = multiprocessing.Process(target=worker_check_fits, args=(data_queue, results_queue, name))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

    # 打印结果
    # while not results_queue.empty():
    #     print(f"Result: {results_queue.get()}")
    print(f'[{results_queue.qsize()}]')

    print("All tasks have been completed.")


