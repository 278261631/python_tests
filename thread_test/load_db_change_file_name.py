import datetime
import multiprocessing
import os
import re
import sqlite3


if __name__ == '__main__':

    date_time_pattern = re.compile(r"UTC(\d{8})_(\d{6})_")
    gy_pattern = re.compile(r"GY(\d)")
    k_pattern = re.compile(r"K(\d+)")

    counter_success = 0
    counter_fail = 0
    db_path_10 = 'fits_wcs_2020_2024.db'
    conn_10 = sqlite3.connect(db_path_10)
    cursor_10 = conn_10.cursor()

    sql_search = f'select id,file_path from  image_info where file_path like "%UTC2023%" and id < 10000000000 limit 300000'
    cursor_10.execute(sql_search)
    db_search_10 = cursor_10.fetchall()

    for line_index, line in enumerate(db_search_10):
        fits_url = line[1]
        fits_id = line[0]
        year_month_day='--'
        hour_minute_second='--'
        match = date_time_pattern.search(fits_url)
        if match:
            year_month_day = match.group(1)  # 年月日
            hour_minute_second = match.group(2)  # 时分秒

        # 提取"K011"和"GY1"
        match = gy_pattern.search(fits_url)
        gy_sys_id = ''
        k_id = ''
        if match:
            gy_sys_id = match.group(1)  # "K011" 或者其他匹配的标识符

        else:
            print(f'---!!no gy')
        match = k_pattern.search(fits_url)
        if match:
            k_id = match.group(1)
        else:
            print(f'---!!no kid')
        # print(f" Date: {year_month_day} Time: {hour_minute_second}  Identifier: {gy_sys_id}  {k_id}")
        fits_id_long = f'{gy_sys_id}{k_id}{year_month_day}{hour_minute_second}'
        if len(fits_id_long) < 18:
            print(f'skip too short {fits_id_long}')
            continue
        fits_short_file_name = f'{fits_id}.fits'
        fits_long_file_name = f'{fits_id_long}.fits'
        fits_short_path = os.path.join('h:/2023/', fits_short_file_name)
        fits_long_path = os.path.join('h:/2023/', fits_long_file_name)
        sql_update_id = f'UPDATE image_info SET id={fits_id_long} WHERE id = {fits_id}'
        if not os.path.exists(fits_short_path):
            print(f'skip not exists {fits_id_long}')
            continue
        os.rename(fits_short_path, fits_long_path)
        print(sql_update_id)
        if line_index % 100 == 0:
            conn_10.commit()
            print(f'process:  {line_index} /   {counter_success} / {counter_fail} / {len(db_search_10)}   ')
        try:
            cursor_10.execute(sql_update_id)
            counter_success = counter_success+1
        except sqlite3.IntegrityError:
            print(f'--  {line[0] }')
            counter_fail = counter_fail+1
            continue

    conn_10.commit()
    cursor_10.close()
    conn_10.close()





