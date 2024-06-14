import multiprocessing
import os
from astropy.coordinates import SkyCoord
import sqlite3
import subprocess
import argparse

import re


def dms_to_deg(d, m, s):
    d_v = float(d)
    m_v = float(m)
    s_v = float(s)
    d_v_abs = abs(d_v)
    sign = 1 if d_v >= 0 else -1
    return sign * (d_v_abs + m_v / 60 + s_v / 3600)


def hms_to_deg(h, m, s):
    h_v = float(h)
    m_v = float(m)
    s_v = float(s)
    return (h_v * 15) + (m_v * 15 / 60) + (s_v * 15 / 3600)


def get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec):
    print(f'hms dms [{src_string_hms_dms}]{len(src_string_hms_dms)}            ra dec[{src_string_ra_dec}]{len(src_string_ra_dec)}')
    assert (len(src_string_hms_dms) > 0 and len(src_string_ra_dec) == 0) or (
                len(src_string_hms_dms) == 0 and len(src_string_ra_dec) > 0)
    src_string = src_string_hms_dms if len(src_string_hms_dms) > 0 else src_string_ra_dec

    cord_array = re.findall(r'\d+(?:\.\d+)?', src_string)
    if not cord_array:
        print(f"座标提取长度错误:  [{src_string}]")
        return

    if len(cord_array) == 2:
        return float(cord_array[0]), float(cord_array[1])
    if len(cord_array) == 6:
        for cord_index, cord_val in enumerate(cord_array):
            print(cord_val)
        hms_ra_deg = hms_to_deg(float(cord_array[0]), float(cord_array[1]), float(cord_array[2]))
        print(f'hms_ra_deg: {hms_ra_deg}')
        dms_dec_deg = dms_to_deg(float(cord_array[3]), float(cord_array[4]), float(cord_array[5]))
        print(f'dms_dec_deg: {dms_dec_deg}')
        return hms_ra_deg, dms_dec_deg
    else:
        print(f"座标提取长度错误:  {len(cord_array)}   [{src_string}]")


# 连接到SQLite数据库
db_path = 'fits_wcs_2020_2024.db'
parser = argparse.ArgumentParser(description='radec 单位是度 ,hms 单位是 时分秒 等. 两个参数只能输入一个')
parser.add_argument('--radec', help='Ra dec deg:(10.5 9.1) 举例 (10.5 9.1) 单位:度')
parser.add_argument('--hms', help='Ra dec :(19:06:49.020 +15:00:34.20)  举例 (19:06:49.020 +15:00:34.20) 单位:时分秒 度分秒')
args = parser.parse_args()
print(f"ra dec: {args.radec}")
print(f"hms : {args.hms}")

hms = args.hms
radec = args.radec
if hms is None:
    hms = ''
if radec is None:
    radec = ''
ra, dec = get_ra_dec_from_string(args.hms, args.radec)

temp_download_path = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}/'
os.makedirs(temp_download_path, exist_ok=True)
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
item_cart = item_coord.cartesian
print(item_cart)
conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
search_sql = f'select id,file_path,wcs_info,center_a_theta, ' \
             f'abs(90-(degrees(acos((({item_cart.x}*t.a_n_x) +({item_cart.y}*t.a_n_y)+({item_cart.z}*t.a_n_z) ))))) as ta,center_b_theta, ' \
             f'abs(90-(degrees(acos((({item_cart.x}*t.b_n_x) +({item_cart.y}*t.b_n_y)+({item_cart.z}*t.b_n_z) ))))) as tb, ' \
             f'degrees(acos((({item_cart.x}*t.center_v_x) +({item_cart.y}*t.center_v_y)+({item_cart.z}*t.center_v_z) ))) as tc ' \
             f'from  image_info as t ' \
             f'where t.status=100 and t.center_a_theta>ta and t.center_b_theta>tb and tc<90'
print(f'{search_sql}')
cursor_search.execute(search_sql)
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()
    for idx, search_item in enumerate(db_search_result):
        data_queue.put(search_item)

        file_name = "{}.fits".format(search_item[0])
        file_name_txt = "{}.txt".format(search_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        save_file_path_txt = os.path.join(temp_download_path, file_name_txt)
        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(f'{search_item[2]}')
        print(f'[{search_item[0]}]:{file_name}        {idx + 1} / {len(db_search_result)}')
        if os.path.exists(save_file_path):
            print(f'[{search_item[0]}]:{file_name}  skip')
            continue
        download_code = 0
        with subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", search_item[1]],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) \
                as proc_down:
            print("the commandline is {}".format(proc_down.args))
            stdout_data, stderr_data = proc_down.communicate()
            if proc_down.returncode == 0:
                download_code = 1
            else:
                download_code = 301
                if stderr_data.decode().__contains__('ERROR 404'):
                    download_code = 404
                print(f'xxx')
        print(f'download = {download_code}  {save_file_path}')







