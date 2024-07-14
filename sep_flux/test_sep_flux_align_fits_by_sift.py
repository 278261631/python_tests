import math
import os

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sep
from PIL import Image
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.visualization import PercentileInterval, LinearStretch, ImageNormalize
from matplotlib.patches import Circle
from skimage.util import img_as_float

from tools.align_tools import find_overlap_by_sep, align_fits_by_light_stars
from tools.ra_dec_tool import get_ra_dec_from_string
from astropy import wcs

matplotlib.use('TkAgg')

src_string_hms_dms = '16:22:54.448 -16:11:0.93'
src_string_ra_dec = ''
ra, dec = get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec)

file_root = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}/'
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)
aligned_fits_path = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}/aligned/'
os.makedirs(aligned_fits_path, exist_ok=True)

align_to_fits_full_path = None
dot_png_align_to_full_path = None
wcs_info_aligned = None
fits_counter = 0
for file_index, file in enumerate(files):
    if file.endswith('.txt'):
        fits_counter = fits_counter + 1
        fits_id = file.replace('.txt', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'{fits_id}.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_full_path = os.path.join(file_root, png_file_name)
        scal_png_full_path = os.path.join(file_root, f'stretch_{fits_id}.png')
        dot_png_full_path = os.path.join(file_root, f'dot_{fits_id}.png')
        key_png_full_path = os.path.join(file_root, f'key_{fits_id}.png')
        mark_png_full_path = os.path.join(file_root, f'mark_{fits_id}.png')
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')
        with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
            line = txt_file.readline()
            wcs_info = wcs.WCS(line)
        # print(f'{line}')
        # print(f'{item_coord}')
        pix_xy = wcs_info.world_to_pixel(item_coord)
        # print(f'pix:   {pix_xy}')

        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()
        # 将16位数据转换为浮点格式
        data = img_as_float(data)

        # Stretch to png
        hist, bin_edges = np.histogram(data, bins=256)
        peak_index = np.argmax(hist)
        peak_value = bin_edges[peak_index]
        interval = PercentileInterval(99.5)  # 这里选择 95% 的范围
        vmin, vmax = interval.get_limits(data)
        # print(f'vmin: {vmin}   vmax:{vmax}')
        stretch = LinearStretch()
        norm = ImageNormalize(data, stretch=stretch, vmin=vmin, vmax=vmax)

        image_data = norm(data) * 255
        image_data = np.clip(image_data, 0, 255)
        image_data = image_data.astype(int)
        print(f'[{np.max(image_data)}]   [{np.min(image_data)}]')

        image_data = image_data.astype(np.uint8)
        # image = Image.fromarray(data)
        image_scal = Image.fromarray(image_data)

        # 保存为PNG图像
        # image.save(png_full_path)
        image_scal.save(scal_png_full_path)

        # data_scal = np.array(image_scal)
        # image_data_np = np.array(image_scal)
        image_data_float = image_data.astype(np.float64)
        # 使用SEP进行源检测
        bkg = sep.Background(image_data_float)
        bkg_image = bkg.back()
        data_no_bg = image_data_float - bkg_image
        objects = sep.extract(data_no_bg, 1.5, err=bkg.globalrms)
        objects = sorted(objects, key=lambda s_obj: s_obj['flux'], reverse=True)
        objects1 = []

        for obj_idx, obj in enumerate(objects):
            if obj_idx < 500:
                objects1.append(obj)
        # for obj in objects:
        #     if obj['flux'] > 5000 or obj['a'] > 100:
        #         objects1.append(obj)
        print(f'objs = {len(objects1)}/{len(objects)}')

        find_overlap_by_sep(scal_png_full_path, key_png_full_path, mark_png_full_path)

        # img1_with_keypoints = data_no_bg.copy()
        # img1_with_keypoints = img1_with_keypoints.astype(np.uint8)
        # for obj1 in objects1:
        #     cv2.circle(img1_with_keypoints, (int(obj1['x']), int(obj1['y'])), int(obj1['a']), (0, 255, 0), 2)
        # # 将图像从BGR转换为RGB
        # img1_with_keypoints = cv2.cvtColor(img1_with_keypoints, cv2.COLOR_BGR2RGB)
        # cv2.imwrite(key_png_full_path, img1_with_keypoints)

        img1_with_dot = np.zeros(data.shape, dtype=np.uint8)
        for obj in objects1:
            cv2.circle(img1_with_dot, (int(obj['x']), int(obj['y'])), 50, (255, 255, 255), -1)
        cv2.imwrite(dot_png_full_path, img1_with_dot)

        if fits_counter == 1:
            align_to_fits_full_path = fits_full_path
            dot_png_align_to_full_path = dot_png_full_path
            wcs_info_aligned = wcs_info
            #     todo copy fits 1
        else:
            # trans_fits_full_path = os.path.join(file_root, f'trans_{fits_id}.fits')
            trans_fits_full_path = os.path.join(aligned_fits_path, f'{fits_id}.fits')
            trans_png_full_path = os.path.join(file_root, f'trans_{fits_id}.png')
            debug_png_full_path = os.path.join(file_root, f'debug_{fits_id}.png')
            align_fits_by_light_stars(fits_full_path, align_to_fits_full_path
                                      , dot_png_full_path, dot_png_align_to_full_path
                                      , trans_fits_full_path, trans_png_full_path, debug_png_full_path, wcs_info_aligned)

        # break
