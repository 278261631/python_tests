import datetime
from solve import config_manager
from solve.scan_by_days import scan_by_day_path
import sqlite3
import concurrent.futures
from threading import Lock

# 连接到SQLite数据库
db_path = config_manager.ini_config.get('database', 'path')
temp_download_path = config_manager.ini_config.get('download', 'temp_download_path')
recent_data = config_manager.ini_config.get('download', 'recent_data') == 'True'

start_day = '20230101'
day_count = 367

lock = Lock()
progress_info = {}
# 最大线程数
max_thread = 10


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


def wget_scan(item_yyyy, item_ymd, identifier):
    # try:
    print(f'[{item_ymd}]:       {identifier} / {len(days_list)}')
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

    with lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        for idx, item in enumerate(file_url_list_all_days):
            cursor.execute('''
                SELECT 1 FROM image_info WHERE file_path = ?
            ''', (item,))
            result = cursor.fetchone()
            if not result:
                cursor.execute('''
                    INSERT INTO image_info (file_path, status)
                    VALUES (?,?)
                ''', (item, 0))
                if idx % 10 == 0:
                    print(f'{idx}/ {len(file_url_list_all_days)} {item}')
        # 提交所有更改
        conn.commit()
        cursor.close()
        conn.close()

    # except Exception as ex:
    #     print(f"An error occurred: {ex}")
    # finally:
    #     with lock:
    #         progress_info[identifier] = 100  # 标记下载完成
    #         print(f"Download {identifier} finished.")


with concurrent.futures.ThreadPoolExecutor(max_workers=max_thread) as executor:
    days_list = calc_days_list(start_day, day_count)
    futures = {executor.submit(wget_scan, r_item[0], r_item[1], i): i for i, r_item in enumerate(days_list)}
    # 等待所有线程任务完成
    for future in concurrent.futures.as_completed(futures):
        identifier_i = futures[future]
        # try:
        future.result()
        # except Exception as e:
        #     print(f"Thread for download {identifier_i} generated an exception: {e}")




