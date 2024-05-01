
import multiprocessing
import os
import shutil

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits

from solve import config_manager
import sqlite3

import subprocess
from astropy import wcs

from solve.test_name_to_ra_dec import get_ra_dec_from_path

# 连接到SQLite数据库
db_path = config_manager.ini_config.get('database', 'path')
temp_download_path = config_manager.ini_config.get('download', 'temp_download_path')


conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
cursor_search.execute('''
    SELECT id, file_path FROM image_info WHERE status = 1 and chk_result=1  limit 30000
''')
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()

# 创建一个锁
mp_lock = multiprocessing.Lock()
# 最大线程数
max_process = 10


def vector_plane_angle(e, n):
    # 计算向量E和法向量N的点积
    dot_product = np.dot(e, n)
    # 计算向量E和法向量N的模
    magnitude_e = np.linalg.norm(e)
    magnitude_n = np.linalg.norm(n)
    # 计算夹角的余弦值
    cos_theta = dot_product / (magnitude_e * magnitude_n)
    # 计算夹角的弧度值
    angle_rad = np.arccos(cos_theta)
    # 将夹角的弧度值转换为度数
    angle_deg_from_rad = np.degrees(angle_rad)
    print(f'dot product    {dot_product}    theta_rad  {angle_rad}  angle_deg   {angle_deg_from_rad}')
    return angle_deg_from_rad


def normalize_vector(vector):
    # 计算向量的模长
    magnitude = np.linalg.norm(vector)
    # 避免除以零的情况
    if magnitude == 0:
        raise ValueError("Cannot normalize a zero vector.")
    # 归一化向量
    normalized_vector = vector / magnitude
    return normalized_vector


def plane_normal_vector(p1, p2, p3):
    # 计算向量V和W
    v = np.array([p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]])
    w = np.array([p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]])
    # 计算叉积，得到法向量N
    n = np.cross(v, w)
    return normalize_vector(n)


def worker_check_fits(d_queue, r_queue, s_queue, p_name):
    while not d_queue.empty():
        try:
            d_item = d_queue.get_nowait()  # 从队列中获取数据
            # print(f'queue num  {d_item}')
        except Exception as e:
            break  # 如果队列为空，则结束进程

        with mp_lock:
            r_queue.put(d_item[0])
        solve_bin_path = r'E:/astap/astap.exe'
        solve_file_path_root = r'E:/test_download/astap/'
        # # 清空目录里的文件
        # if os.path.exists(solve_file_path_root):
        #     entries = os.listdir(solve_file_path_root)
        #     for entry in entries:
        #         full_path = os.path.join(solve_file_path_root, entry)
        #         if os.path.isfile(full_path) or os.path.islink(full_path):
        #             os.remove(full_path)
        #             print(f'-not remove  {full_path}')
        file_name = "{}.fits".format(d_item[0])
        file_name_wcs = "{}.wcs".format(d_item[0])
        file_name_ini = "{}.ini".format(d_item[0])
        wcs_file_path = os.path.join(solve_file_path_root, file_name_wcs)
        ini_file_path = os.path.join(solve_file_path_root, file_name_ini)
        download_file_path = os.path.join(temp_download_path, file_name)
        solve_file_path = os.path.join(solve_file_path_root, file_name)
        print(f'process:  {r_queue.qsize()+1}/{s_queue.qsize()} / {len(db_search_result)}    '
              f'{d_item[0]}    {d_item[1]}   [{p_name}]')
        # 拷贝文件
        try:
            shutil.copy(download_file_path, solve_file_path)
        except IOError:
            with mp_lock:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                sql_str = f'UPDATE image_info SET status=-1 WHERE id = {d_item[0]}'
                print(sql_str)
                cursor.execute(sql_str)
                conn.commit()
                cursor.close()
                conn.close()
            continue
        astap_ra_h, astap_dec = get_ra_dec_from_path(d_item[1])
        astap_dec_spd = astap_dec + 90
        process = subprocess.Popen([solve_bin_path, '-ra', str(astap_ra_h), '-spd', str(astap_dec_spd),
                                    '-s', '800',
                                    '-z', '2', '-fov', '2', '-D', 'd50', '-r', '60', '-f',
                                    solve_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print("the commandline is {}".format(process.args))
        print(" ".join(process.args))
        process.communicate()
        process.wait()
        if process.returncode == 0:
            print("tycho was successful.")
        else:
            with mp_lock:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                print("tycho failed.")
                print("Error message:", process.stderr)
                sql_str = f'UPDATE image_info SET status=101 WHERE id = {d_item[0]}'
                print(sql_str)
                cursor.execute(sql_str)
                conn.commit()
                cursor.close()
                conn.close()
                os.remove(solve_file_path)
                os.remove(ini_file_path)
                continue
        # 检测wcs

        # 读取文本文件并解析每一行以提取头信息

        header_dict = {}
        with open(wcs_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('END') and '=' in line:
                    if '/' in line:
                        comment_index = line.index('/')
                        line = line[:comment_index]
                    line = line.replace("'", "")
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 尝试将值转换为适当的数据类型
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        # 如果转换失败，保留原始字符串值
                        pass

                    header_dict[key] = value

        wcs_info = wcs.WCS(header_dict)

        print(wcs_info)
        header_string = wcs_info.to_header_string()
        print(header_string)
        # wcs_info_load = wcs.WCS(header_string)
        print('-----------------')
        print(wcs_info.wcs.crval)
        print(f'{len(wcs_info.wcs.crpix)}    {wcs_info.wcs.crpix}')
        if wcs_info.wcs.crpix[0] < 2 or wcs_info.wcs.crpix[1] < 2:
            with mp_lock:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                print(f'-------- skip crpix = 0  {d_item[0]}    {d_item[1]} ---------')
                sql_str = f'UPDATE image_info SET status=101 WHERE id = {d_item[0]}'
                print(sql_str)
                cursor.execute(sql_str)
                conn.commit()
                cursor.close()
                conn.close()
                os.remove(solve_file_path)
                os.remove(ini_file_path)

            # os.remove(solve_file_path)
            continue
        try:
            print(wcs_info.wcs.cd)
        except Exception as e:
            print(f"错误: {e}")
            print(f'-------- skip wcs.cd error  {d_item[0]}    {d_item[1]} ---------')
            os.remove(solve_file_path)
            os.remove(ini_file_path)
            os.remove(wcs_file_path)
            continue
        print('-----------------')

        with fits.open(solve_file_path) as fits_hdul:
            hdul = fits_hdul
            image_data = hdul[0].data
        # 获取图像的宽度和高度
        width, height = image_data.shape[1], image_data.shape[0]
        print(f'x: {width}  y:{height}    x/2 {(width + 1) / 2}   y/2 {(height + 1) / 2}')
        # 获取x y中点
        ra_mid_x, dec_mid_x = wcs_info.wcs_pix2world((width + 1) / 2, 0, 1)
        ra_mid_y, dec_mid_y = wcs_info.wcs_pix2world(0, (height + 1) / 2, 1)
        #  tycho 的识别结果有时候不是以图像中心点为 crpix ,会有少量偏移?
        ra_mid_img, dec_mid_img = wcs_info.wcs_pix2world((width + 1) / 2, (height + 1) / 2, 1)
        ra_corner_img, dec_corner_img = wcs_info.wcs_pix2world(0, 0, 1)
        print(
            f'x_mid: {ra_mid_x}  {dec_mid_x}    y_mid: {ra_mid_y}  {dec_mid_y}   img_mid: {ra_mid_img}  {dec_mid_img}  ')
        # 获取x y 中点 图像中心点image_c test_target cartesian坐标
        coord_img_center = SkyCoord(ra=ra_mid_img, dec=dec_mid_img, unit='deg')
        cartesian_img_center = coord_img_center.cartesian
        coord_img_corner = SkyCoord(ra=ra_corner_img, dec=dec_corner_img, unit='deg')
        cartesian_img_corner = coord_img_corner.cartesian
        coord_mid_x = SkyCoord(ra=ra_mid_x, dec=dec_mid_x, unit='deg')
        cartesian_mid_x = coord_mid_x.cartesian
        coord_mid_y = SkyCoord(ra=ra_mid_y, dec=dec_mid_y, unit='deg')
        cartesian_mid_y = coord_mid_y.cartesian
        print(f'center {coord_img_center}   {cartesian_img_center}   ')
        o_center = [0, 0, 0]
        img_center = [cartesian_img_center.x, cartesian_img_center.y, cartesian_img_center.z]
        img_x_center = [cartesian_mid_x.x, cartesian_mid_x.y, cartesian_mid_x.z]
        img_y_center = [cartesian_mid_y.x, cartesian_mid_y.y, cartesian_mid_y.z]
        plane_normal_vector_x = plane_normal_vector(o_center, img_center, img_x_center)
        plane_normal_vector_y = plane_normal_vector(o_center, img_center, img_y_center)
        target_vector = [cartesian_img_corner.x, cartesian_img_corner.y, cartesian_img_corner.z]

        theta_deg_corner_to_x = vector_plane_angle(target_vector, plane_normal_vector_x)
        theta_deg_corner_to_x = abs(90 - theta_deg_corner_to_x)
        print(f'v {cartesian_img_corner}  {plane_normal_vector_x}')
        print(
            f"img corner to x_plan deg: {theta_deg_corner_to_x}   {coord_mid_y}  {cartesian_mid_y}  to {cartesian_img_center} ")

        theta_deg_corner_to_y = vector_plane_angle(target_vector, plane_normal_vector_y)
        theta_deg_corner_to_y = abs(90 - theta_deg_corner_to_y)
        print(f'v {cartesian_img_corner}  {plane_normal_vector_y}')
        print(
            f"img corner to y_plan deg: {theta_deg_corner_to_y}   {coord_mid_y}  {cartesian_mid_y}  to {cartesian_img_center} ")
        with mp_lock:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            sql_str = f'UPDATE image_info SET status=100, wcs_info ="{wcs_info.to_header_string()}", center_v_x={cartesian_img_center.x},' \
                      f' center_v_y={cartesian_img_center.y}, center_v_z={cartesian_img_center.z},' \
                      f' a_v_x={cartesian_mid_x.x}, a_v_y={cartesian_mid_x.y}, a_v_z={cartesian_mid_x.z},' \
                      f'center_a_theta={theta_deg_corner_to_x},' \
                      f' b_v_x={cartesian_mid_y.x}, b_v_y={cartesian_mid_y.y}, b_v_z={cartesian_mid_y.z}, ' \
                      f'center_b_theta={theta_deg_corner_to_y},' \
                      f'a_n_x={plane_normal_vector_x[0]}, a_n_y={plane_normal_vector_x[1]},a_n_z={plane_normal_vector_x[2]},' \
                      f'b_n_x={plane_normal_vector_y[0]}, b_n_y={plane_normal_vector_y[1]},b_n_z={plane_normal_vector_y[2]}' \
                      f'  WHERE id = {d_item[0]}'
            print(sql_str)

            cursor.execute(sql_str)
            conn.commit()
            cursor.close()
            conn.close()
            # 删除文件
            os.remove(solve_file_path)
            os.remove(wcs_file_path)
            os.remove(ini_file_path)
            s_queue.put(d_item[0])


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    results_queue = multiprocessing.Queue()
    success_queue = multiprocessing.Queue()
    for search_item in db_search_result:
        data_queue.put(search_item)
    processes = []

    # 启动进程
    for i in range(max_process):
        name = f"p_{i+1}"
        proc = multiprocessing.Process(target=worker_check_fits, args=(data_queue, results_queue, success_queue, name))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

    # 打印结果
    # while not results_queue.empty():
    #     print(f"Result: {results_queue.get()}")
    print(f'[{results_queue.qsize()}]')

    print("All tasks have been completed.")


