import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sep
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from matplotlib.patches import Circle
from skimage import color, morphology
from skimage.util import img_as_float

from tools.ra_dec_tool import get_ra_dec_from_string
from astropy import wcs
matplotlib.use('TkAgg')


src_string_hms_dms = '16:22:54.448 -16:11:0.93'
src_string_ra_dec = ''
ra, dec = get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec)

file_root = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}_align/'
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)
img_sub_x_wid = 400
img_sub_y_wid = 300

source_map = {}
for file_index, file in enumerate(files):
    if file.endswith('.fits'):
        fits_id = file.replace('.fits', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'{fits_id}.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_full_path = os.path.join(file_root, png_file_name)
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')
        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()
        # 将16位数据转换为浮点格式
        # data = img_as_float(data)
        data = data.astype(np.float32)
        wcs_info = wcs.WCS(hdu[0].header)
        pix_xy = wcs_info.world_to_pixel(item_coord)
        print(f'pix:   {pix_xy}')

        # 使用SEP进行源检测
        # data = data.byteswap().newbyteorder()
        bkg = sep.Background(data)
        bkg_image = bkg.back()
        data_no_bg = data - bkg_image
        objects = sep.extract(data_no_bg, 6, err=bkg.globalrms)
        print(f'objs = {len(objects)}')

        height, width = data.shape
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

        print(f'---{fits_id} --  {start_x}  {end_x} [{end_x - start_x}]            {start_y} {end_y} [{end_y - start_y}]')
        region = data_no_bg[start_y:end_y, start_x:end_x]
        # 创建一个新的图像数组，大小为期望的尺寸，初始填充为0（或其他背景值）
        new_image = np.zeros((img_sub_y_wid, img_sub_x_wid), dtype=data.dtype)

        new_image[y_offset:y_offset + region.shape[0], x_offset:x_offset + region.shape[1]] = region

        fig, ax = plt.subplots()
        ax.imshow(new_image, cmap='gray')

        circle = Circle((mark_position_x, mark_position_y), 10, edgecolor='green', facecolor='none', linewidth=0.4)
        ax.add_patch(circle)

        # 在图像上为每个源绘制圆圈
        for obj in objects:
            # 圆圈的中心位置
            s_center_x = obj['x']
            s_center_y = obj['y']
            if center_x-100 < s_center_x < center_x+100 and center_y-100 < s_center_y < center_y+100:
                s_center_x = s_center_x - start_x + x_offset
                s_center_y = s_center_y - start_y + y_offset
                # 圆圈的半径，这里使用a参数的一半作为圆圈半径
                radius = obj['a'] * 4.0
                # 绘制圆圈
                circle = plt.Circle((s_center_x, s_center_y), radius, color='red', fill=False, linewidth=0.2)
                ax.add_patch(circle)
                # wcs_info.pixel_to_world([[s_center_x, s_center_y]])
                item_cord = wcs_info.wcs_pix2world(obj['x'], obj['y'], 0)
                # wcs_info.wcs_pix2world([[obj['x'], obj['y']]])
                # s_key = f'{item_cord[0]:.3f}_{item_cord[1]:.3f}'
                key_area_mask = 0b11111110
                key_cord_0 = math.floor(item_cord[0]*1000) & key_area_mask
                key_cord_1 = math.floor(item_cord[1]*1000) & key_area_mask
                s_key = f'{key_cord_0}_{key_cord_1}'

                # print(f'ra_dec pixel_to_world      {item_cord} {item_cord[0]:}_{item_cord[1]}  {s_key} ')
                # item_ra, item_dec = wcs_info.pixel_to_world([[obj['x'], obj['y']]])[0]
                # print(f'ra_dec pixel_to_world   {item_ra}   {item_dec}')
                if s_key not in source_map:
                    source_map[s_key] = [[fits_id, obj['x'], obj['y'], s_center_x, s_center_y, obj['flux'], obj['a']]]
                else:
                    source_map[s_key].append([fits_id, obj['x'], obj['y'], s_center_x, s_center_y, obj['flux'], obj['a']])

        ax.axis('off')

        plt.savefig(png_full_path, dpi=300, format='png', bbox_inches='tight')
        plt.close(fig)
        # break
# print(source_map)
sorted_items = sorted(source_map.items(), key=lambda item: len(item[1]), reverse=True)
sorted_dict = dict(sorted_items)
# print(sorted_dict)
flux_txt_full_path = os.path.join(file_root, 'sep_flux_list.log')
with open(flux_txt_full_path, 'w', encoding='utf-8') as file:
    for key, value in sorted_dict.items():
        # 将键值对写入文件，键和值之间用等号连接，然后换行
        file.write(f"{key} = {value}\n")

for file_index, file in enumerate(files):
    if file.endswith('.fits'):
        fits_id = file.replace('.fits', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'all_{fits_id}.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_all_full_path = os.path.join(file_root, png_file_name)
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')

        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()
        # 将16位数据转换为浮点格式
        data = img_as_float(data)
        wcs_info = wcs.WCS(hdu[0].header)
        pix_xy = wcs_info.world_to_pixel(item_coord)
        print(f'pix:   {pix_xy}')

        height, width = data.shape
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

        print(f'---{fits_id} --  {start_x}  {end_x} [{end_x - start_x}]            {start_y} {end_y} [{end_y - start_y}]')
        region = data[start_y:end_y, start_x:end_x]
        # 创建一个新的图像数组，大小为期望的尺寸，初始填充为0（或其他背景值）
        new_image = np.zeros((img_sub_y_wid, img_sub_x_wid), dtype=data.dtype)

        new_image[y_offset:y_offset + region.shape[0], x_offset:x_offset + region.shape[1]] = region

        fig, ax = plt.subplots()
        ax.imshow(new_image, cmap='gray')

        # circle = Circle((mark_position_x, mark_position_y), 10, edgecolor='green', facecolor='none', linewidth=0.4)
        # ax.add_patch(circle)

        # 在图像上为每个源绘制圆圈
        for item_key, item_value in sorted_dict.items():
            for val_index, sources_val in enumerate(item_value):

                s_center_x = sources_val[3]
                s_center_y = sources_val[4]
                if fits_id == sources_val[0]:
                    # 圆圈的半径，这里使用a参数的一半作为圆圈半径
                    radius = sources_val[6] * 3.0
                    # 绘制圆圈
                    len_src = len(item_value)
                    color = 'yellow'
                    text_shift = 3
                    if len_src > 1:
                        color = (0.5, 0.5, 0.5)
                    plt.text(x=s_center_x+text_shift, y=s_center_y+text_shift, s=f'({len_src})_{item_key}', color=color, fontsize=4, ha='center', va='center')
                    circle = plt.Circle((s_center_x, s_center_y), radius, color=color, fill=False, linewidth=0.2)
                    ax.add_patch(circle)

        ax.axis('off')

        plt.savefig(png_all_full_path, dpi=300, format='png', bbox_inches='tight')
        plt.close(fig)
        # break

