import datetime
import os
from math import sqrt
import numpy as np
import sep
from astropy.io import fits
from skimage.exposure import histogram
from skimage.feature import blob_dog
from solve import config_manager
import sqlite3
import concurrent.futures
import subprocess
from threading import Lock

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
    SELECT id, file_path FROM image_info WHERE status = 0   limit 100
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

lock = Lock()
progress_info = {}
# 最大线程数
max_thread = 3


def calc_days_list(yyyymmdd_str, day_count_param):
    # 创建开始日期
    year = int(yyyymmdd_str[:4])
    month = int(yyyymmdd_str[4:6])
    day = int(yyyymmdd_str[6:])
    start_date = datetime.datetime(year, month, day)
    scan_day_list = []
    # 遍历日期区间
    for single_date in range(day_count_param):
        # 获取当前日期
        current_date = start_date + datetime.timedelta(days=single_date)
        yyyy = current_date.strftime('%Y')
        yyyymmdd = current_date.strftime('%Y%m%d')
        print(current_date.strftime('%Y-%m-%d'))
        print(f'{yyyy}   {yyyymmdd}')
        scan_day_list.append([yyyy, yyyymmdd])
    return scan_day_list


def wget_download(search_result, identifier):
    file_name = "{}.fits".format(search_result[0])
    save_file_path = os.path.join(temp_download_path, file_name)
    print(f'[{search_result[0]}]:{file_name}       {identifier} / {len(db_search_result)}')
    with subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", search_result[1]],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) \
            as proc:
        print("the commandline is {}".format(proc.args))
        proc.communicate()

        if proc.returncode == 0:
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
            # blobs_dog = blob_dog(data, max_sigma=30, threshold=0.05)
            # blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
            # blog_num = len(blobs_dog)
            # all_check_pass = exp_check_pass and (blog_num > 200)
            image_data_float = data.astype(np.float64)
            bkg = sep.Background(image_data_float)
            data_sub = image_data_float - bkg
            objects = sep.extract(data_sub, 10, err=bkg.globalrms)
            sep_obj_len = len(objects)
            all_check_pass = exp_check_pass and (sep_obj_len > 200)

            with lock:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                sql_str = f'UPDATE image_info SET status=1,' \
                          f'chk_exp_hist={1 if exp_check_pass else -1},blob_dog_num={sep_obj_len},' \
                          f'chk_result =  {1 if all_check_pass else -1},status=1 ' \
                          f'WHERE id = {search_result[0]}'
                cursor.execute(sql_str)
                conn.commit()
                cursor.close()
                conn.close()
            pass
        else:
            print("Download failed.")
            print("Error message:", proc.stderr)


with concurrent.futures.ThreadPoolExecutor(max_workers=max_thread) as executor:
    futures = {executor.submit(wget_download, r_item, i): i for i, r_item in enumerate(db_search_result)}
    # 等待所有线程任务完成
    for future in concurrent.futures.as_completed(futures):
        identifier_i = futures[future]
        # try:
        future.result()
        # except Exception as e:
        #     print(f"Thread for download {identifier_i} generated an exception: {e}")




