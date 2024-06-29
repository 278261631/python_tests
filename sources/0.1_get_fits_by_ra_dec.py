import multiprocessing
import os
from astropy.coordinates import SkyCoord
import sqlite3
import subprocess
import argparse
from tools.ra_dec_tool import get_ra_dec_from_string

# 连接到SQLite数据库
db_path = 'fits_wcs_2020_2024.db'
# db_path = 'fits_wcs_recent.db'

parser = argparse.ArgumentParser(description='radec 单位是度 ,Hms 单位是 时分秒 等. 两个参数只能输入一个')
parser.add_argument('--radec', help='Ra dec deg:(10.5 9.1) 举例 (10.5 9.1) 单位:度')
parser.add_argument('--Hms', help='Ra dec :(19:06:49.020 +15:00:34.20)  举例 (19:06:49.020 +15:00:34.20) 单位:时分秒 度分秒')
args = parser.parse_args()
print(f"ra dec: {args.radec}")
print(f"Hms : {args.Hms}")

src_string_hms_dms = '16:22:54.448 -16:11:0.93'
src_string_ra_dec = ''
ra, dec = get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec)

temp_download_path = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}_recent/'
# temp_download_path = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}/'
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
             f'where t.status=100 and t.center_a_theta>ta and t.center_b_theta>tb and tc<90 limit 30'
print(f'{search_sql}')
cursor_search.execute(search_sql)
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

max_process = 1


def worker_download_fits(d_queue, r_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程
        file_name = "{}.fits".format(d_item[0])
        file_name_txt = "{}.txt".format(d_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        save_file_path_txt = os.path.join(temp_download_path, file_name_txt)
        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(f'{d_item[2]}')
        print(f'[{d_item[0]}]:{file_name}       {p_name} {r_queue.qsize()+1} / {len(db_search_result)}')
        if os.path.exists(save_file_path):
            print(f'[{d_item[0]}]:{file_name}  skip')
            r_queue.put(d_item[0])
            continue
        download_code = 0
        with subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", d_item[1]],
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
        r_queue.put(d_item[0])  # 将结果放回结果队列


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()
    for search_item in db_search_result:
        data_queue.put(search_item)
    processes = []

    # 启动进程
    for i in range(max_process):
        name = f"p_{i+1}"
        proc = multiprocessing.Process(target=worker_download_fits, args=(data_queue, results_queue, name))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

    print(f'r_size {results_queue.qsize()}')

    print("All tasks have been completed.")


