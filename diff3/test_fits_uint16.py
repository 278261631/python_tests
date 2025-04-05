import cv2
import numpy as np
from astropy.io import fits
from astropy.visualization import ImageNormalize, MinMaxInterval
from mpmath import norm


def process_fits_image(data, header=None):
    # 创建新Header对象避免污染原始头信息
    new_header = fits.Header() if header is None else header.copy()

    # 1.处理FITS数据缩放（保留原始标定参数）
    if header:
        bscale = header.get('BSCALE', 1.0)
        bzero = header.get('BZERO', 0.0)
        data = data * bscale + bzero
        # 更新标定参数到新header
        new_header['BSCALE'] = (1.0, 'Data scaling factor')
        new_header['BZERO'] = (32768, 'Data offset for unsigned int')

    # 2.处理无效值（保留极值信息）
    valid_mask = np.isfinite(data)
    if not np.all(valid_mask):
        data = np.where(valid_mask, data, np.percentile(data[valid_mask], 50))  # 用中值替换异常值

    # 3.动态范围优化（适应16bit存储）
    data_min = np.min(data[valid_mask])
    data_max = np.max(data[valid_mask])

    # 线性映射到0-65535范围（保留1%头尾数据防止异常拉伸）
    lower = np.percentile(data, 1)
    upper = np.percentile(data, 99)
    scaled_data = np.clip((data - lower) / (upper - lower) * 65535, 0, 65535).astype(np.uint16)

    return fits.PrimaryHDU(data=scaled_data, header=new_header)


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


# 生成HDU对象
hdu_ok = process_fits_image(hdulist_ok[0].data, hdulist_ok[0].header)
hdu_er = process_fits_image(hdulist_er[0].data, hdulist_er[0].header)


# 保存为FITS文件
hdu_ok.writeto('output_ok.fits', overwrite=True)
hdu_er.writeto('output_er.fits', overwrite=True)
