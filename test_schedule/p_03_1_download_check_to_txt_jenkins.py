import argparse
import concurrent
import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import sep
from astropy.io import fits
from skimage.exposure import histogram

from tools.send_message import ProcessStatus, send_amq

#  拥挤在过曝区域 %5
threshold_percentage_95 = 95
# 拥挤在低曝光 3% 的范围
threshold_percentage_10 = 2


fits_list_chk = []


def worker_check_fits(d_queue, folder_name, max_workers=8):
    temp_download_path = f'e:/fix_data/{folder_name}'
    d_queue_size = len(d_queue)

    def process_item(d_item):
        index = 0

        file_name = "{}.fits".format(d_item[0])
        file_name_txt = "{}_chk.txt".format(d_item[0])
        file_name_solve = "{}_solve.txt".format(d_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        save_file_path_txt = os.path.join(temp_download_path, file_name_txt)
        save_file_path_solve = os.path.join(temp_download_path, file_name_solve)
        print(f'[{d_item[0]}]:{file_name}        {index + 1} / {d_queue_size}')
        send_amq(f'{d_item[0]}.fits', 3, ProcessStatus.DEFAULT)
        if os.path.exists(save_file_path_solve):
            send_amq(f'{d_item[0]}.fits', 3, ProcessStatus.SKIP)
            return
        if os.path.exists(save_file_path_txt):
            print(f'SS')
            send_amq(f'{d_item[0]}.fits', 3, ProcessStatus.SKIP)
            return
        try:
            with fits.open(save_file_path) as hdul:
                # 假设数据在第一个 HDU 中
                data = hdul[0].data
        except (FileNotFoundError, OSError):
            print(f'-1  file not found{save_file_path}')
            with open(save_file_path_txt, 'w', encoding='utf-8') as file:
                file.write(f'{file_name_txt},{1},{-1},{-1},{-1},{d_item[0]}')
            return
        hist, bin_edges = histogram(data)
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
        except (FileNotFoundError, Exception) as e:
            print(e)
            print(f'err:  {d_item[0]}  {d_item[1]}')

            print(f'-1  file not found{save_file_path}')
            with open(save_file_path_txt, 'w', encoding='utf-8') as file:
                file.write(f'{file_name_txt},{1},{-1},{-1},{-1},{d_item[0]}')
            return
        sep_obj_len = len(objects)
        all_check_pass = exp_check_pass and (sep_obj_len > 200)
        print(f'exp {exp_check_pass}   sep_obj {sep_obj_len}    all {all_check_pass}')

        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(
                f'{file_name_txt},{1},{1 if exp_check_pass else -1},{sep_obj_len},{1 if all_check_pass else -1},{d_item[0]}')
        print(f'{"++" if all_check_pass else "--"}')

    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, data_item in enumerate(d_queue):
            future = executor.submit(process_item, data_item)
            futures.append(future)
            # 设置超时时间为10秒
        timeout = 60
        try:
            for future_item in as_completed(futures, timeout=timeout):

                result = future_item.result()
                print(result)
        except concurrent.futures.TimeoutError:
            print("任务执行超时")
        except Exception as e:
            print(f"任务出现异常: {e}")


def run_03_check_to_txt(folder_name):
    temp_download_path = f'e:/fix_data/{folder_name}'
    if not os.path.exists(temp_download_path):
        return
    files = os.listdir(temp_download_path)
    for file_index, fits_file in enumerate(files):
        if fits_file.endswith('.fits'):
            fits_full_path = os.path.join(temp_download_path, fits_file)
            fits_name = os.path.splitext(fits_file)
            assert len(fits_name) == 2
            fits_list_chk.append([fits_name[0], fits_full_path])

    data_queue = []
    print(f'len: {len(fits_list_chk)}')
    for idx, search_item in enumerate(fits_list_chk):
        file_name_txt_chk = "{}_chk.txt".format(search_item[0])
        file_name_txt_ok = "{}_ok.txt".format(search_item[0])
        file_name_download = "{}.fits".format(search_item[0])
        save_file_path_txt_chk = os.path.join(temp_download_path, file_name_txt_chk)
        save_file_path_txt_ok = os.path.join(temp_download_path, file_name_txt_ok)
        save_file_path_download = os.path.join(temp_download_path, file_name_download)

        if not os.path.exists(save_file_path_txt_ok):
            print(f'ss {idx}  {save_file_path_txt_ok}')
            continue
        if os.path.exists(save_file_path_txt_chk):
            print(f'ss {idx}  {save_file_path_txt_chk}')
        else:
            if os.path.exists(save_file_path_download):
                print(f'++ {idx}')
                data_queue.append(search_item)
            else:
                print(f'-- {idx}')

    worker_check_fits(data_queue, folder_name)


def parse_args():
    parser = argparse.ArgumentParser(description="Schedule job with optional time parameter.")
    parser.add_argument('--time', type=str, help='time in YYYYMMDD format')
    return parser.parse_args()


def main():
    current_time = datetime.datetime.now()
    args = parse_args()
    if args.time:
        try:
            current_time = datetime.datetime.strptime(args.time, '%Y%m%d')
        except ValueError:
            print("Invalid time format. Please use YYYYMMDD.")

    folder_name = current_time.strftime('%Y%m%d')
    run_03_check_to_txt(folder_name)


if __name__ == "__main__":
    main()
