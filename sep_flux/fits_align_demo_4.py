import os

import matplotlib
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from astropy.wcs import WCS
import matplotlib.pyplot as plt
from reproject import reproject_interp

from tools.ra_dec_tool import get_ra_dec_from_string

matplotlib.use('TkAgg')

# file_root = f'src_process/test_2/'
file_root = f'src_process/245.726867_-16.18359167/'
file_out_root = f'src_process/245.726867_-16.18359167_align/'
os.makedirs(file_out_root, exist_ok=True)
files = os.listdir(file_root)

hdu1 = None
wcs1 = None
hdu2 = None
wcs2 = None

file_counter = 0
for file_index, file in enumerate(files):
    if file.endswith('.txt'):
        file_counter = file_counter + 1
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
        # print(f'{line}')
        # print(f'{item_coord}')

        if file_counter == 1:
            wcs1 = wcs_info
            hdu1_list = fits.open(get_pkg_data_filename(fits_full_path))
            hdu1 = hdu1_list[0]
            hdu1.header.update(wcs1.to_header())
            first_fits_full_path = os.path.join(file_out_root, f'{fits_id}.fits')
            hdu1_list.writeto(first_fits_full_path)
            hdu1_list.close()  # 关闭原始FITS文件
            # print(wcs1)
            # print(hdu1)
        else:
            wcs2 = wcs_info
            hdu2 = fits.open(get_pkg_data_filename(fits_full_path))[0]
            hdu2.header.update(wcs2.to_header())
            # print(wcs2)
            # print(hdu2)
            # hdu = fits.open(fits_full_path)
            # data = hdu[0].data
            # hdu.close()
            # 将16位数据转换为浮点格式
            # data = img_as_float(data)

            array, footprint = reproject_interp(hdu2, hdu1.header)
            rep_fits_full_path = os.path.join(file_out_root, f'{fits_id}.fits')
            fits.writeto(rep_fits_full_path, array, hdu1.header)
