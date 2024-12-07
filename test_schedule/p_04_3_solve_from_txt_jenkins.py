import argparse
import datetime
import os
import sqlite3

import ctypes

from tools.send_message import ProcessStatus, send_amq


def output_debug_string(message):
    ctypes.windll.kernel32.OutputDebugStringW(message)


def run_p_09_clean_dir(folder_name):

    # 连接到SQLite数据库
    db_path = '../thread_test/fits_wcs_recent.db'
    temp_txt_path = f'e:/fix_data/{folder_name}/'
    conn_search = sqlite3.connect(db_path)
    cursor_search = conn_search.cursor()
    if not os.path.exists(temp_txt_path):
        return
    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        if file.endswith('_solve.txt'):
            txt_full_path = os.path.join(temp_txt_path, file)
            with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
                line = txt_file.readline()
                parts = line.split(',')
                # print(parts)
                # print(parts[20])
            len_parts = len(parts)
            if len_parts != 24:
                for i, item in enumerate(parts):
                    print(f'{i}:  {item}')
            if parts[2] != '100':
                print(f'ss: {file_index}')
                continue
            assert len_parts == 24
            send_amq(f'{parts[23]}.fits', 43, ProcessStatus.DEFAULT)
            sql_search = f'select id,file_path from  image_info where id = {parts[23]} and status=100 and image_info.wcs_info is not null limit 1'
            print(sql_search)
            cursor_search.execute(sql_search)
            db_search_result = cursor_search.fetchall()
            if len(db_search_result) == 1:
                file_name_fits = os.path.join(temp_txt_path, f'{parts[23]}.fits')
                file_name_txt_ok = os.path.join(temp_txt_path, f'{parts[23]}_ok.txt')
                file_name_txt_chk = os.path.join(temp_txt_path, f'{parts[23]}_chk.txt')
                print(f'del : {file_name_fits}    {file_name_txt_ok}    {file_name_txt_chk}')
                try:
                    os.remove(file_name_fits)
                    os.remove(file_name_txt_ok)
                    os.remove(file_name_txt_chk)
                except OSError as e:
                    print(f"Error: {e.strerror} - {e.filename}")
                # todo
            send_amq(f'{parts[23]}.fits', 43, ProcessStatus.SUCCESS)
    cursor_search.close()
    conn_search.close()


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
    run_p_09_clean_dir(folder_name)


if __name__ == "__main__":
    main()





