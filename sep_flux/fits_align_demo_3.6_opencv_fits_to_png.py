import math
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sep
from PIL import Image
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.visualization import ZScaleInterval, ImageNormalize, AsinhStretch, PercentileInterval, LinearStretch
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

        hist, bin_edges = np.histogram(data, bins=256)
        peak_index = np.argmax(hist)
        peak_value = bin_edges[peak_index]

        # 4. 使用 PercentileInterval 选择拉伸范围
        interval = PercentileInterval(99.5)  # 这里选择 95% 的范围
        vmin, vmax = interval.get_limits(data)
        print(f'vmin: {vmin}   vmax:{vmax}')

        # 5. 使用 LinearStretch 进行线性拉伸
        stretch = LinearStretch()
        norm = ImageNormalize(data, stretch=stretch, vmin=vmin, vmax=vmax)

        image_data = norm(data) * 255
        image_data = np.clip(image_data, 0, 255)
        image_data = image_data.astype(int)
        print(f'[{np.max(image_data)}]   [{np.min(image_data)}]')

        image_data = image_data.astype(np.uint8)
        # 4. 使用 PIL 创建图像
        # image = Image.fromarray(image_data)
        image = Image.fromarray(data)
        image_scal = Image.fromarray(image_data)

        # 保存为PNG图像
        image.save(png_full_path)
        image_scal.save(scal_png_full_path)

