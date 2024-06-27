from astropy.io import fits
import numpy as np

# 指定FITS文件路径
fits_file_path = f'E:/fix_data/light_1.fits'
output_fits_file_path = 'sub_fits.fits'

# 打开FITS文件
with fits.open(fits_file_path) as hdul:
    # 读取数据，假设数据存储在第一个HDU中
    image_data = hdul[0].data
    cropped_data = image_data[800:1600, 800:1600]

    new_hdu = fits.PrimaryHDU(cropped_data)
    hdul_new = fits.HDUList(new_hdu)
    hdul_new.writeto(output_fits_file_path, overwrite=True)
    print(f"截取的图像已保存到 {output_fits_file_path}")
