import math
import os

import matplotlib
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

matplotlib.use('TkAgg')

file_root = r'e:/src_process/10.500000_10.10000000/'
ra = 10.5
dec = 10.1
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)
img_sub_x_wid = 4800
img_sub_y_wid = 3211

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
        px = math.floor(pix_xy[0])
        py = math.floor(pix_xy[1])
        x_start = math.floor(px - (img_sub_x_wid/2))
        y_start = math.floor(py - (img_sub_y_wid/2))
        x_start = x_start if x_start >= 0 else 0
        y_start = y_start if y_start >= 0 else 0
        x_end = x_start + img_sub_x_wid
        y_end = y_start + img_sub_y_wid
        # todo 右下越界修正

        mark_position_x = px - x_start
        mark_position_y = py - y_start

        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()
        region = data[y_start:y_end, x_start:x_end]

        fig, ax = plt.subplots()
        ax.imshow(region, cmap='gray')  # 对于灰度图像使用 'gray' colormap

        # 添加红色圆圈标记
        # 假设我们知道要标记的圆心坐标和半径
        circle = Circle((mark_position_x, mark_position_y), 10, edgecolor='red', facecolor='none')
        ax.add_patch(circle)

        # 保存图像到本地文件
        plt.savefig(png_full_path, bbox_inches='tight')
        plt.close(fig)
        # 关闭FITS文件

