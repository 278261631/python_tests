import argparse
import datetime
import os
import re
from solve.scan_by_days import scan_by_day_path
import sqlite3
import concurrent.futures

from tools.send_message import send_amq, ProcessStatus

# 连接到SQLite数据库
db_path = '../thread_test/fits_wcs_recent.db'
recent_data = True
day_count = 1


def check_urls_txt(date_ymd):
    temp_download_path = f'e:/fix_data/{date_ymd}/'
    file_name_txt_url = "{}_urls.txt".format(date_ymd)
    save_file_path_url = os.path.join(temp_download_path, file_name_txt_url)
    print(f'check {save_file_path_url}')
    if not os.path.exists(save_file_path_url):
        return False
    with open(save_file_path_url, 'r', encoding='utf-8') as txt_file:
        lines = txt_file.readlines()

    len_parts = len(lines)
    if len_parts < 30:
        for i, item in enumerate(lines):
            print(f'{i}:  {item}')
        return False

    return True


def save_fits_list(fits_url_list, date_ymd):
    temp_download_path = f'e:/fix_data/{date_ymd}/'
    file_name_txt_ok = "{}_urls.txt".format(date_ymd)
    save_file_path_ok = os.path.join(temp_download_path, file_name_txt_ok)

    save_file_dir = temp_download_path
    if not os.path.exists(save_file_path_ok):
        print(f'+{save_file_path_ok}')
        os.makedirs(save_file_dir, exist_ok=True)
        with open(save_file_path_ok, 'w', encoding='utf-8') as file:
            for url_item in fits_url_list:
                file.write(f'{url_item}\r\n')
                # file.write(f'{url_item}{os.linesep}')
    else:
        print(f'skip-{save_file_path_ok}')


def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y%m%d')
        return True
    except ValueError:
        return False


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
        scan_day_list.append([yyyy, yyyymmdd])
    return scan_day_list


def wget_scan(item_yyyy, item_ymd):
    file_url_list_all_days = []
    send_amq(f'gy1.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY1-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    send_amq(f'gy2.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY2-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    send_amq(f'gy3.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY3-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    send_amq(f'gy4.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY4-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    send_amq(f'gy5.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY5-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    send_amq(f'gy6.fits', 1, ProcessStatus.DEFAULT)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY6-DATA')
    file_url_list_all_days.extend(url_list_by_day)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    date_time_pattern = re.compile(r"UTC(\d{8})_(\d{6})_")
    gy_pattern = re.compile(r"GY(\d)")
    k_pattern = re.compile(r"K(\d+)")
    insert_counter = 0

    for idx, item in enumerate(file_url_list_all_days):
        sql_str = f'SELECT 1 FROM image_info WHERE file_path = "{item}"'
        print(f'{idx}    {item}')
        cursor.execute(sql_str)
        print(f'--? [  {item_ymd}  ]:{idx}/ {len(file_url_list_all_days)} {item}  ')
        result = cursor.fetchone()
        if not result:
            print(f'--pass [  {item_ymd}  ]:{idx}/ {len(file_url_list_all_days)} {item}  ')
            # 使用正则表达式提取年月日时分秒
            match = date_time_pattern.search(item)
            if match:
                year_month_day = match.group(1)  # 年月日
                hour_minute_second = match.group(2)  # 时分秒

            # 提取"K011"和"GY1"
            match = gy_pattern.search(item)
            gy_sys_id = ''
            k_id = ''
            if match:
                gy_sys_id = match.group(1)  # "K011" 或者其他匹配的标识符

            else:
                print(f'---!!no gy')
            match = k_pattern.search(item)
            if match:
                k_id = match.group(1)
            else:
                print(f'---!!no kid')
            # print(f" Date: {year_month_day} Time: {hour_minute_second}  Identifier: {gy_sys_id}  {k_id}")
            sql_str = f'INSERT INTO image_info (id, file_path, status) VALUES ({gy_sys_id}{k_id}' \
                      f'{year_month_day}{hour_minute_second},"{item}",{0})'
            print(f' [  {item_ymd}  ]:{idx}/ {len(file_url_list_all_days)}  {sql_str}')
            insert_counter = insert_counter+1
            cursor.execute(sql_str)
            # if idx % 10 == 0:
            #     print(f'{idx}/ {len(file_url_list_all_days)} {item}')
        else:
            print(f'--x [  {item_ymd}  ]:{idx}/ {len(file_url_list_all_days)} {item} ')
        # 提交所有更改
        conn.commit()
    cursor.close()
    conn.close()

    save_fits_list(file_url_list_all_days, item_ymd)

    return insert_counter


def run_01_scan(start_day, folder_name):

    if check_urls_txt(start_day):
        print(f'skip  {start_day}')
        return
    print(f'scan  {start_day}')
    conn_search_date = sqlite3.connect(db_path)
    cursor_search_date = conn_search_date.cursor()
    sql_search_date = f'select substr(id, 5, 8) AS id_substring from  image_info order by id_substring desc limit 1'
    cursor_search_date.execute(sql_search_date)
    db_search_result_date = cursor_search_date.fetchall()
    cursor_search_date.close()
    conn_search_date.close()
    max_date_str = db_search_result_date[0][0]
    if not validate_date(max_date_str):
        print(f'日期无效 {max_date_str}')
        exit(1)

    print(f'start from [{start_day}]')

    days_list = calc_days_list(start_day, day_count)
    insert_counter = 0
    for i, r_item in enumerate(days_list):
        insert_counter = wget_scan(r_item[0], r_item[1])


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
            print("Invalid time format. Please use YYYYMMDD_HHMMSS.")

    folder_name = current_time.strftime('%Y%m%d')
    run_01_scan(folder_name, folder_name)


if __name__ == "__main__":
    main()


