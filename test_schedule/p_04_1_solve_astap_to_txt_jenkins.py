import argparse
import concurrent
import datetime
import multiprocessing
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
import subprocess
from astropy import wcs
from solve.test_name_to_ra_dec import get_ra_dec_from_path
import ctypes

from tools.send_message import ProcessStatus, send_amq


def output_debug_string(message):
    ctypes.windll.kernel32.OutputDebugStringW(message)


fits_list = []


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
    # print(f'dot product    {dot_product}    theta_rad  {angle_rad}  angle_deg   {angle_deg_from_rad}')
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


def worker_check_fits(d_item, folder_name):
    temp_download_path = f'e:/fix_data/{folder_name}/'

    solve_bin_path = r'E:/astap/astap.exe'
    solve_file_path_root = r'E:/test_download/astap/'
    file_name = "{}.fits".format(d_item[0])
    file_name_wcs = "{}.wcs".format(d_item[0])
    file_name_ini = "{}.ini".format(d_item[0])
    wcs_file_path = os.path.join(solve_file_path_root, file_name_wcs)
    ini_file_path = os.path.join(solve_file_path_root, file_name_ini)
    download_file_path = os.path.join(temp_download_path, file_name)
    solve_file_path = os.path.join(solve_file_path_root, file_name)
    file_name_txt = "{}_solve.txt".format(d_item[0])
    save_file_path_txt = os.path.join(temp_download_path, file_name_txt)
    print(f'process:  / /     '
          f'{d_item[0]}.fits    {d_item[1]}   ')
    output_debug_string(f"solve: {d_item[0]}.fits， {d_item[1]}")
    # 拷贝文件
    try:
        shutil.copy(download_file_path, solve_file_path)
    except IOError:
        print(f'-1  file not found{download_file_path}')
        return
    fack_url_path = f'K{d_item[0][1:4]}_K{d_item[0][1:4]}'
    astap_ra_h, astap_dec = get_ra_dec_from_path(fack_url_path)
    astap_dec_spd = astap_dec + 90
    process = subprocess.Popen([solve_bin_path, '-ra', str(astap_ra_h), '-spd', str(astap_dec_spd),
                                # process = subprocess.Popen([solve_bin_path, '-ra', '106', '-spd', '141',
                                '-s', '1000',
                                '-z', '1', '-fov', '2', '-D', 'd50', '-r', '180', '-f',
                                solve_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print("the commandline is {}".format(process.args))
    print(" ".join(process.args))
    print("子进程PID:", process.pid)

    try:
        process.communicate(timeout=60)
        # process.wait(6)
        process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        print("子进程超时，将被终止")
        try:
            os.kill(process.pid, 9)  # 发送SIGKILL信号（9）来强制终止进程
        except ProcessLookupError:
            print("子进程已经退出")
        except Exception as e:
            print(f"子进程已经退出 pid:{process.pid}  path {d_item[0]}.fits {e}")
            os.kill(process.pid, 9)  # 发送SIGKILL信号（9）来强制终止进程
    if process.returncode == 0:
        # print("tycho was successful.")
        if not os.path.exists(wcs_file_path):
            print(f'-1  file not found{wcs_file_path}')
            os.remove(solve_file_path)
            return
    else:
        print(f'astap error {download_file_path}')
        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(f'{file_name_txt},{d_item[0]},{101}')
        os.remove(solve_file_path)
        os.remove(ini_file_path)
        return
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

    # print(wcs_info)
    header_string = wcs_info.to_header_string()
    # print(header_string)
    # wcs_info_load = wcs.WCS(header_string)
    # print('-----------------')
    # print(wcs_info.wcs.crval)
    # print(f'{len(wcs_info.wcs.crpix)}    {wcs_info.wcs.crpix}')
    if wcs_info.wcs.crpix[0] < 2 or wcs_info.wcs.crpix[1] < 2:
        print(f'wcs chk error {download_file_path}')
        with open(save_file_path_txt, 'w', encoding='utf-8') as file:
            file.write(f'{file_name_txt},{d_item[0]},{101}')
        os.remove(solve_file_path)
        os.remove(ini_file_path)
        return
    try:
        print(wcs_info.wcs.cd)
    except Exception as e:
        print(f"错误: {e}")
        print(f'-------- skip wcs.cd error  {d_item[0]}    {d_item[1]} ---------')
        os.remove(solve_file_path)
        os.remove(ini_file_path)
        os.remove(wcs_file_path)
        return
    # print('-----------------')

    with fits.open(solve_file_path) as fits_hdul:
        hdul = fits_hdul
        image_data = hdul[0].data
    # 获取图像的宽度和高度
    width, height = image_data.shape[1], image_data.shape[0]
    # print(f'x: {width}  y:{height}    x/2 {(width + 1) / 2}   y/2 {(height + 1) / 2}')
    # 获取x y中点
    ra_mid_x, dec_mid_x = wcs_info.wcs_pix2world((width + 1) / 2, 0, 1)
    ra_mid_y, dec_mid_y = wcs_info.wcs_pix2world(0, (height + 1) / 2, 1)
    #  tycho 的识别结果有时候不是以图像中心点为 crpix ,会有少量偏移?
    ra_mid_img, dec_mid_img = wcs_info.wcs_pix2world((width + 1) / 2, (height + 1) / 2, 1)
    ra_corner_img, dec_corner_img = wcs_info.wcs_pix2world(0, 0, 1)
    # print(
    #     f'x_mid: {ra_mid_x}  {dec_mid_x}    y_mid: {ra_mid_y}  {dec_mid_y}   img_mid: {ra_mid_img}  {dec_mid_img}  ')
    # 获取x y 中点 图像中心点image_c test_target cartesian坐标
    coord_img_center = SkyCoord(ra=ra_mid_img, dec=dec_mid_img, unit='deg')
    cartesian_img_center = coord_img_center.cartesian
    coord_img_corner = SkyCoord(ra=ra_corner_img, dec=dec_corner_img, unit='deg')
    cartesian_img_corner = coord_img_corner.cartesian
    coord_mid_x = SkyCoord(ra=ra_mid_x, dec=dec_mid_x, unit='deg')
    cartesian_mid_x = coord_mid_x.cartesian
    coord_mid_y = SkyCoord(ra=ra_mid_y, dec=dec_mid_y, unit='deg')
    cartesian_mid_y = coord_mid_y.cartesian
    # print(f'center {coord_img_center}   {cartesian_img_center}   ')
    o_center = [0, 0, 0]
    img_center = [cartesian_img_center.x, cartesian_img_center.y, cartesian_img_center.z]
    img_x_center = [cartesian_mid_x.x, cartesian_mid_x.y, cartesian_mid_x.z]
    img_y_center = [cartesian_mid_y.x, cartesian_mid_y.y, cartesian_mid_y.z]
    plane_normal_vector_x = plane_normal_vector(o_center, img_center, img_x_center)
    plane_normal_vector_y = plane_normal_vector(o_center, img_center, img_y_center)
    target_vector = [cartesian_img_corner.x, cartesian_img_corner.y, cartesian_img_corner.z]

    theta_deg_corner_to_x = vector_plane_angle(target_vector, plane_normal_vector_x)
    theta_deg_corner_to_x = abs(90 - theta_deg_corner_to_x)
    # print(f'v {cartesian_img_corner}  {plane_normal_vector_x}')
    # print(
    #     f"img corner to x_plan deg: {theta_deg_corner_to_x}   {coord_mid_y}  {cartesian_mid_y}  to {cartesian_img_center} ")

    theta_deg_corner_to_y = vector_plane_angle(target_vector, plane_normal_vector_y)
    theta_deg_corner_to_y = abs(90 - theta_deg_corner_to_y)
    # print(f'v {cartesian_img_corner}  {plane_normal_vector_y}')
    # print(
    #     f"img corner to y_plan deg: {theta_deg_corner_to_y}   {coord_mid_y}  {cartesian_mid_y}  to {cartesian_img_center} ")

    with open(save_file_path_txt, 'w', encoding='utf-8') as file:
        file.write(f'{file_name_txt},{d_item[0]},{100},{wcs_info.to_header_string()},{cartesian_img_center.x},'
                   f'{cartesian_img_center.y},{cartesian_img_center.z},'
                   f'{cartesian_mid_x.x},{cartesian_mid_x.y},{cartesian_mid_x.z},'
                   f'{theta_deg_corner_to_x},'
                   f'{cartesian_mid_y.x},{cartesian_mid_y.y},{cartesian_mid_y.z},'
                   f'{theta_deg_corner_to_y},'
                   f'{plane_normal_vector_x[0]},{plane_normal_vector_x[1]},{plane_normal_vector_x[2]},'
                   f'{plane_normal_vector_y[0]},{plane_normal_vector_y[1]},{plane_normal_vector_y[2]},'
                   f'{d_item[0]}')
    # print(sql_str)

    # 删除文件
    os.remove(solve_file_path)
    os.remove(wcs_file_path)
    os.remove(ini_file_path)
    send_amq(f'{d_item[0]}.fits', 4, ProcessStatus.SUCCESS)
    print(f'process:  / / {len(fits_list)}    '
          f'{d_item[0]}.fits    {d_item[0]}  ')


def run_p_04_1_solve_astap_to_txt(folder_name, max_workers=8):
    temp_download_path = f'e:/fix_data/{folder_name}/'
    if not os.path.exists(temp_download_path):
        return
    files = os.listdir(temp_download_path)
    for file_index, fits_file in enumerate(files):
        if fits_file.endswith('.fits'):
            fits_full_path = os.path.join(temp_download_path, fits_file)
            fits_name = os.path.splitext(fits_file)
            assert len(fits_name) == 2
            fits_list.append([fits_name[0], fits_full_path])

    print(f'len: {len(fits_list)}')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for search_item in fits_list:
            file_name_txt_solve = "{}_solve.txt".format(search_item[0])
            file_name_download = "{}.fits".format(search_item[0])
            save_file_path_txt_solve = os.path.join(temp_download_path, file_name_txt_solve)
            save_file_path_download = os.path.join(temp_download_path, file_name_download)
            send_amq(f'{search_item[0]}.fits', 4, ProcessStatus.DEFAULT)
            if os.path.exists(save_file_path_txt_solve):
                send_amq(f'{search_item[0]}.fits', 4, ProcessStatus.SKIP)
                print(f'ss  {save_file_path_txt_solve}')
            else:
                if os.path.exists(save_file_path_download):
                    print(f'++')
                    future = executor.submit(worker_check_fits, search_item, folder_name)
                    futures.append(future)
                else:
                    print(f'--')
        timeout = 60
        try:
            for future_item in as_completed(futures, timeout=timeout):

                result = future_item.result()
                print(result)
        except concurrent.futures.TimeoutError:
            print("任务执行超时")
            future_item.cancel()
        except Exception as e:
            print(f"任务出现异常: {e}")


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
    run_p_04_1_solve_astap_to_txt(folder_name)


if __name__ == "__main__":
    main()


