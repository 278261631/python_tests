import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pywt
from skimage import restoration
from astropy.io import fits  # 导入用于读取FITS文件的模块
from skimage.util import img_as_float  # 导入用于将图像转换为浮点格式的函数
matplotlib.use('TkAgg')


def plot_result(image, background):
    fig, ax = plt.subplots(nrows=1, ncols=3)

    ax[0].imshow(image, cmap='gray')
    ax[0].set_title('Original image')
    ax[0].axis('off')

    ax[1].imshow(background, cmap='gray')
    ax[1].set_title('Background')
    ax[1].axis('off')

    ax[2].imshow(image - background, cmap='gray')
    ax[2].set_title('Result')
    ax[2].axis('off')

    fig.tight_layout()


# 读取FITS文件
# fits_file = f'sub_fits.fits'
fits_file = f'w_hat_r.fits'
with fits.open(fits_file) as hdul:
    image_FITS = hdul[0].data  # 假设数据存储在HDU 0中

# 将16位数据转换为浮点格式
image_fits = img_as_float(image_FITS)

# 应用滚动球算法估计背景
background = restoration.rolling_ball(image_fits)
# 计算结果图像
result_image = image_fits - background

# 创建包含背景和结果图像的HDU列表
hdu_background_p = fits.PrimaryHDU(background)
hdu_background = fits.HDUList(hdu_background_p)

hdu_result_p = fits.PrimaryHDU(result_image)
hdu_result = fits.HDUList(hdu_result_p)

background_fits_file = 'bg_rb_background.fits'
result_fits_file = 'bg_rb_result.fits'

hdu_background.writeto(background_fits_file, overwrite=True)
print(f'Background image saved as {background_fits_file}')

hdu_result.writeto(result_fits_file, overwrite=True)
print(f'Result image saved as {result_fits_file}')
# 绘制结果
plot_result(image_fits, background)
plt.show()


print(f'--')

