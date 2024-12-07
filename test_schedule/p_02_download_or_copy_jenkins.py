import argparse
import datetime
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from tools.fits_check import copy_or_download
import ctypes

from tools.send_message import send_amq, ProcessStatus


def output_debug_string(message):
    ctypes.windll.kernel32.OutputDebugStringW(message)


def worker_download_fits(db_search_result, folder_name):
    temp_download_path = f'e:/fix_data/{folder_name}/'
    file_in_disk_path_root = 'e:/'
    save_file_dir = temp_download_path

    if not os.path.exists(save_file_dir):
        os.makedirs(save_file_dir, exist_ok=True)

    def download_task(d_item):
        file_name = "{}.fits".format(d_item[0])
        file_name_txt_ok = "{}_ok.txt".format(d_item[0])
        file_name_txt_solve = "{}_solve.txt".format(d_item[0])

        save_file_path = os.path.join(temp_download_path, file_name)
        save_file_path_ok = os.path.join(temp_download_path, file_name_txt_ok)
        save_file_path_solve = os.path.join(temp_download_path, file_name_txt_solve)

        file_in_disk_path = os.path.join(file_in_disk_path_root, file_name)

        print(f'[{d_item[0]}]:{file_name}')
        download_code = 0
        output_debug_string(f"download: {d_item[0]}.fits， {file_name}")
        send_amq(f'{d_item[0]}.fits', 2, ProcessStatus.DEFAULT)
        if os.path.exists(save_file_path_solve):
            send_amq(f'{d_item[0]}.fits', 2, ProcessStatus.SKIP)
            return
        if os.path.exists(save_file_path_ok):
            send_amq(f'{d_item[0]}.fits', 2, ProcessStatus.SKIP)
            return
        success = copy_or_download(save_file_path, d_item[1], file_in_disk_path)
        if success:
            with open(save_file_path_ok, 'w', encoding='utf-8') as file:
                file.write(f'{d_item[0]},ok')
            send_amq(f'{d_item[0]}.fits', 2, ProcessStatus.SUCCESS)

    with ThreadPoolExecutor(max_workers=2) as executor:
        for i, d_item in enumerate(db_search_result):
            executor.submit(download_task, d_item)
            print(f'[{i} / {len(db_search_result)}]')


def run_02_download(date_str):
    db_path = '../thread_test/fits_wcs_recent.db'
    conn_search = sqlite3.connect(db_path)
    cursor_search = conn_search.cursor()
    # todo limit date
    sql_search = f'select id,file_path from  image_info where file_path like "%UTC{date_str}%" limit 5000'
    print(f'---search sql    {sql_search}')
    cursor_search.execute(sql_search)
    db_search_result = cursor_search.fetchall()
    cursor_search.close()
    conn_search.close()
    worker_download_fits(db_search_result, date_str)


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
    output_debug_string(f"download: {folder_name}")
    run_02_download(folder_name)


if __name__ == "__main__":
    main()

