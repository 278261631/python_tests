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


src_string_hms_dms = '16:22:54.448 -16:11:0.93'
src_string_ra_dec = ''
ra, dec = get_ra_dec_from_string(src_string_hms_dms, src_string_ra_dec)

file_root = f'src_process/{ra:0>3.6f}_{dec:0>2.8f}/'
# file_root = r'e:/src_process/20.500000_20.10000000_small/'
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)
img_sub_x_wid = 400
img_sub_y_wid = 300
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
        pix_xy = wcs_info.world_to_pixel(item_coord)
        print(f'pix:   {pix_xy}')
        if file_counter == 1:
            wcs1 = wcs_info
            hdu1 = fits.open(get_pkg_data_filename(fits_full_path))[0]
            print(wcs1)
            print(hdu1)
        else:
            wcs2 = wcs_info
            hdu2 = fits.open(get_pkg_data_filename(fits_full_path))[0]
            print(wcs1)
            print(hdu1)
            # hdu = fits.open(fits_full_path)
            # data = hdu[0].data
            # hdu.close()
            # 将16位数据转换为浮点格式
            # data = img_as_float(data)

            array, footprint = reproject_interp(hdu2, hdu1.header)
            rep_fits_full_path = os.path.join(file_root, f'rep_{fits_id}.fits')
            fits.writeto(rep_fits_full_path, array, hdu1.header, overwrite=True)
