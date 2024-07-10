import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sep
from PIL import Image
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.visualization import ZScaleInterval, ImageNormalize
from matplotlib.patches import Circle
from skimage.util import img_as_float

from tools.ra_dec_tool import get_ra_dec_from_string
from astropy import wcs
matplotlib.use('TkAgg')

file_root = f'src_process/test_/'
files = os.listdir(file_root)

source_map = {}
for file_index, file in enumerate(files):
    if file.endswith('.fits'):
        fits_id = file.replace('.fits', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'{fits_id}.png'
        scal_png_file_name = f's_{fits_id}.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_full_path = os.path.join(file_root, png_file_name)
        scal_png_full_path = os.path.join(file_root, scal_png_file_name)
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')
        # 打开FITS文件
        hdu = fits.open(fits_full_path)

        # 获取图像数据，假设它存储在主HDU中
        data = hdu[0].data
        hdu.close()

        # data = data.astype(np.float32)
        # bkg = sep.Background(data)
        # bkg_image = bkg.back()
        # data_no_bg = data - bkg_image

        interval = ZScaleInterval()
        vmin, vmax = interval.get_limits(data)
        image_data = (data - vmin) / (vmax - vmin) * 255
        image_data = np.clip(image_data, 0, 255)
        image_data = image_data.astype(int)

        # 4. 使用 PIL 创建图像
        # image = Image.fromarray(image_data)
        image = Image.fromarray(data)
        image_scal = Image.fromarray(image_data)

        # 保存为PNG图像
        image.save(png_full_path)
        image_scal.save(scal_png_full_path)

