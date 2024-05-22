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
db_path = 'fits_wcs_2022_789.db'
temp_download_path = 'e:/2022_789/'
#  拥挤在过曝区域 %5
threshold_percentage_95 = 95
# 拥挤在低曝光 3% 的范围
threshold_percentage_10 = 2
temp_txt_path = 'c:/2022_789'


conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
# SELECT id, file_path FROM image_info WHERE status = 1 and chk_result is  null    limit 200000
cursor_search.execute('''
    SELECT id, file_path FROM image_info WHERE status = 1 and chk_result is  null    limit 40000
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

# 最大线程数
max_process = 12


def worker_check_fits(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            # print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程
        file_name = "{}.fits".format(d_item[0])
        file_name_txt = "{}.txt".format(d_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        save_file_path_txt = os.path.join(temp_txt_path, file_name_txt)
        print(f'[{d_item[0]}]:{file_name}       {p_name} {r_queue.qsize() + 1} / {len(db_search_result)}')
        if os.path.exists(save_file_path_txt):
            print(f'SS')
            continue
        try:
            with fits.open(save_file_path) as hdul:
                # 假设数据在第一个 HDU 中
                data = hdul[0].data
        except (FileNotFoundError, OSError):
            print(f'-1  file not found{save_file_path}')
            with open(save_file_path_txt, 'w', encoding='utf-8') as file:
                file.write(f'{file_name_txt},{1},{-1},{-1},{-1},{d_item[0]}')
            continue
        hist, bin_edges = histogram(data)
        # print(f'{len(hist)}   {len(bin_edges)}')
        # 计算直方图的累积分布函数 (CDF)
        cdf = np.cumsum(hist) / np.sum(hist)
        threshold_index_95 = int(threshold_percentage_95 / 100 * len(cdf))
        threshold_index_10 = int(threshold_percentage_10 / 100 * len(cdf))
        is_overexposed = cdf[-1] - cdf[threshold_index_95] > 0.9
        is_underexposed = cdf[-1] - cdf[threshold_index_10] < 0.1
        exp_check_pass = not (is_underexposed or is_overexposed)
        # print(f'cdf {cdf[-1]}   95 {cdf[threshold_index_95]}    10 {cdf[threshold_index_10]}')
        # print(f'under {is_underexposed}   over {is_overexposed}    exp {exp_check_pass}')
        image_data_float = data.astype(np.float64)
        bkg = sep.Background(image_data_float)
        data_sub = image_data_float - bkg
        try:
            objects = sep.extract(data_sub, 10, err=bkg.globalrms)
        except (FileNotFoundError, Exception) as e:
            print(e)
            print(f'err:  {d_item[0]}  {d_item[1]}')

            print(f'-1  file not found{save_file_path}')
            with open(save_file_path_txt, 'w', encoding='utf-8') as file:
                file.write(f'{file_name_txt},{1},{-1},{-1},{-1},{d_item[0]}')
            continue
        sep_obj_len = len(objects)
        all_check_pass = exp_check_pass and (sep_obj_len > 200)
        print(f'exp {exp_check_pass}   sep_obj {sep_obj_len}    all {all_check_pass}')

        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(f'{file_name_txt},{1},{1 if exp_check_pass else -1},{sep_obj_len},{1 if all_check_pass else -1},{d_item[0]}')
        print(f'{"++" if all_check_pass else "--"}')
        # sql_str = f'UPDATE image_info SET status=1,' \
        #           f'chk_exp_hist={1 if exp_check_pass else -1},blob_dog_num={sep_obj_len},' \
        #           f'chk_result =  {1 if all_check_pass else -1} ' \
        #           f'WHERE id = {d_item[0]}'

        # print(f'{sql_str}')
        # print(f"Process {p_name}  [{r_queue.qsize()}]has finished processing data: ")
        r_queue.put(p_name)  # 将结果放回结果队列


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()
    for search_item in db_search_result:
        file_name_txt_chk = "{}.txt".format(search_item[0])
        save_file_path_txt_chk = os.path.join(temp_txt_path, file_name_txt_chk)
        if not os.path.exists(save_file_path_txt_chk):
            data_queue.put(search_item)
        else:
            print(f'SS  ')
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


