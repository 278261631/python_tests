import cv2
import numpy as np
from astropy.io import fits
from astropy.visualization import ImageNormalize, MinMaxInterval
from mpmath import norm


def process_fits_image(data, header=None):
    # 1.处理FITS数据缩放
    if header:
        bscale = header.get('BSCALE', 1.0)
        bzero = header.get('BZERO', 0.0)
        data = data * bscale + bzero

    # 2.处理无效值
    data = np.nan_to_num(data, nan=0.0, posinf=np.nanmax(data), neginf=np.nanmin(data))

    # 3.专业归一化处理
    norm = ImageNormalize(data, interval=MinMaxInterval())
    return np.uint8(norm(data) * 255)


fits_ok = f'../diff/GY1_K035-4_C_60S_Bin2_UTC20240623_193150_-13.1C__pp_ref_cut1.fits'
fits_er = f'../diff2/GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp_ref_cut1.fits'

# 加载fits_ok fits_er并保存为jpg
# fits_ok_jpg = fits_ok.replace('.fits', '.jpg')
# fits_er_jpg = fits_er.replace('.fits', '.jpg')
fits_ok_jpg = f'ok.jpg'
fits_er_jpg = f'er.jpg'

# 读取fits文件
hdulist_ok = fits.open(fits_ok)
hdulist_er = fits.open(fits_er)


# 应用处理函数
image_ok = process_fits_image(hdulist_ok[0].data, hdulist_ok[0].header)
image_er = process_fits_image(hdulist_er[0].data, hdulist_er[0].header)

# 将图像数据转换为uint8类型
# image_ok = np.uint8(image_ok)
# image_er = np.uint8(image_er)
# image_ok = np.uint8(norm(image_ok) * 255)
# image_er = np.uint8(norm(image_er) * 255)

# 保存为jpg文件
cv2.imwrite(fits_ok_jpg, image_ok)
cv2.imwrite(fits_er_jpg, image_er)
