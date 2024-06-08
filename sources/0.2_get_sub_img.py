import math
import os

import matplotlib
import numpy as np
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

matplotlib.use('TkAgg')

file_root = r'e:/src_process/20.500000_20.10000000_small/'
ra = 20.5
dec = 20.1
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)
# img_sub_x_wid = 4800
# img_sub_y_wid = 3211
img_sub_x_wid = 400
img_sub_y_wid = 300

for file_index, file in enumerate(files):
    if file.endswith('.txt'):
        fits_id = file.replace('.txt', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'{fits_id}.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_full_path = os.path.join(file_root, png_file_name)
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')
        with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
            line = txt_file.readline()
            wcs_info = wcs.WCS(line)
        print(f'{line}')
        print(f'{item_coord}')
        pix_xy = wcs_info.world_to_pixel(item_coord)
        print(f'pix:   {pix_xy}')
        # px = math.floor(pix_xy[0])
        # py = math.floor(pix_xy[1])
        # x_start = math.floor(px - (img_sub_x_wid/2))
        # y_start = math.floor(py - (img_sub_y_wid/2))
        # x_start = x_start if x_start >= 0 else 0
        # y_start = y_start if y_start >= 0 else 0
        #
        # x_end = x_start + img_sub_x_wid
        # y_end = y_start + img_sub_y_wid

        # mark_position_x = px - x_start
        # mark_position_y = py - y_start

        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()
        height, width = data.shape
        # y_start = y_start if y_start + y_end <= height else 0
        # x_start = x_start if x_start + x_end <= width else 0

        center_x = pix_xy[0]
        center_y = pix_xy[1]
        start_x = max(center_x - img_sub_x_wid // 2, 0)
        end_x = min(center_x + img_sub_x_wid // 2 + img_sub_x_wid % 2, width)
        start_y = max(center_y - img_sub_y_wid // 2, 0)
        end_y = min(center_y + img_sub_y_wid // 2 + img_sub_y_wid % 2, height)
        start_x = math.floor(start_x)
        start_y = math.floor(start_y)
        end_x = math.floor(end_x)
        end_y = math.floor(end_y)

        x_offset = abs(min(center_x - img_sub_x_wid // 2, 0))
        y_offset = abs(min(center_y - img_sub_y_wid // 2, 0))
        x_offset = math.floor(x_offset)
        y_offset = math.floor(y_offset)

        mark_position_x = center_x - start_x + x_offset
        mark_position_y = center_y - start_y + y_offset

        print(f'{start_x}  {end_x} [{end_x - start_x}]            {start_y} {end_y} [{end_y - start_y}]')
        region = data[start_y:end_y, start_x:end_x]
        # region = data[x_start:x_end, y_start:y_end]
        # print(f'{x_start}  {x_end} [{x_end - x_start}]            {y_start} {y_end} [{y_end - y_start}]')
        # 创建一个新的图像数组，大小为期望的尺寸，初始填充为0（或其他背景值）
        new_image = np.zeros((img_sub_y_wid, img_sub_x_wid), dtype=data.dtype)

        # 确定截取图像在新数组中的位置
        # x_offset = (img_sub_x_wid - (end_x - start_x)) // 2
        # y_offset = (img_sub_y_wid - (end_y - start_y)) // 2
        new_image[y_offset:y_offset + region.shape[0], x_offset:x_offset + region.shape[1]] = region

        fig, ax = plt.subplots()
        ax.imshow(new_image, cmap='gray')  # 对于灰度图像使用 'gray' colormap

        # 添加红色圆圈标记
        # 假设我们知道要标记的圆心坐标和半径
        circle = Circle((mark_position_x, mark_position_y), 10, edgecolor='red', facecolor='none')
        ax.add_patch(circle)

        # 保存图像到本地文件
        plt.savefig(png_full_path, bbox_inches='tight')
        plt.close(fig)
        # 关闭FITS文件


