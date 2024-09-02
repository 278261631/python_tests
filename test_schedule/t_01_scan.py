import datetime
import re
from solve.scan_by_days import scan_by_day_path
import sqlite3
import concurrent.futures


# 连接到SQLite数据库
db_path = '../thread_test/fits_wcs_recent.db'
recent_data = True
day_count = 1


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
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY1-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY2-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY3-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY4-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY5-DATA')
    file_url_list_all_days.extend(url_list_by_day)
    url_list_by_day = scan_by_day_path(item_yyyy, item_ymd, recent_data, sys_name_root='GY6-DATA')
    file_url_list_all_days.extend(url_list_by_day)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    date_time_pattern = re.compile(r"UTC(\d{8})_(\d{6})_")
    gy_pattern = re.compile(r"GY(\d)")
    k_pattern = re.compile(r"K(\d+)")
    insert_counter = 0
    for idx, item in enumerate(file_url_list_all_days):
        cursor.execute('''
            SELECT 1 FROM image_info WHERE file_path = ?
        ''', (item,))
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
    return insert_counter


def run_01_scan():
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
    start_day = (datetime.datetime.strptime(max_date_str, '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d')
    start_day = '20240828'
    print(f'start from [{start_day}]')
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    current_date_dt = datetime.datetime.strptime(current_date, '%Y%m%d')

    start_day_dt = datetime.datetime.strptime(start_day, '%Y%m%d')
    if start_day_dt > current_date_dt:
        return

    days_list = calc_days_list(start_day, day_count)
    insert_counter = 0
    for i, r_item in enumerate(days_list):
        insert_counter = wget_scan(r_item[0], r_item[1])
    if 0 == insert_counter:
        for j in range(1, 10):
            start_day = (datetime.datetime.strptime(start_day, '%Y%m%d') + datetime.timedelta(days=1)).strftime('%Y%m%d')
            print(f'start from [{start_day}]')
            start_day_dt = datetime.datetime.strptime(start_day, '%Y%m%d')
            if start_day_dt > current_date_dt:
                return
            days_list.clear()
            days_list = calc_days_list(start_day, day_count)
            for i, r_item in enumerate(days_list):
                insert_counter = wget_scan(r_item[0], r_item[1])
            if insert_counter != 0:
                break

            current_date = datetime.datetime.now().strftime('%Y%m%d')
            start_day_dt = datetime.datetime.strptime(start_day, '%Y%m%d')
            current_date_dt = datetime.datetime.strptime(current_date, '%Y%m%d')

            if start_day_dt > current_date_dt:
                break



