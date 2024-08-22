import multiprocessing
import os
import sqlite3
from tools.fits_check import copy_or_download
from tools.regex_from_string import get_yyyy_from_path

# 连接到SQLite数据库
db_path = '../sources/fits_wcs_recent.db'
temp_download_path = 'e:/fix_data/'
file_in_disk_path_root = 'e:/'


def worker_download_fits(db_search_result):
    for i, d_item in enumerate(db_search_result):
        file_name = "{}.fits".format(d_item[0])
        file_name_txt_ok = "{}_ok.txt".format(d_item[0])
        yyyy = get_yyyy_from_path(d_item[1])
        save_file_path = os.path.join(temp_download_path, yyyy, file_name)
        save_file_path_ok = os.path.join(temp_download_path, yyyy, file_name_txt_ok)

        save_file_dir = os.path.join(temp_download_path, yyyy)
        # print(f'?{file_in_disk_dir}')
        if not os.path.exists(save_file_dir):
            print(f'+{save_file_dir}')
            os.makedirs(save_file_dir, exist_ok=True)
        file_in_disk_path = os.path.join(file_in_disk_path_root, yyyy, file_name)
        print(f'[{d_item[0]}]:{file_name}       {i} / {len(db_search_result)}')
        download_code = 0
        success = copy_or_download(save_file_path, d_item[1], file_in_disk_path)
        if success:
            with open(save_file_path_ok, 'w', encoding='utf-8') as file:
                file.write(f'{d_item[0]},ok')


def run_02_download():
    conn_search = sqlite3.connect(db_path)
    cursor_search = conn_search.cursor()
    sql_search = f'select id,file_path from  image_info where status = 0 and image_info.wcs_info is null limit 3'
    cursor_search.execute(sql_search)
    db_search_result = cursor_search.fetchall()
    cursor_search.close()
    conn_search.close()
    worker_download_fits(db_search_result)
