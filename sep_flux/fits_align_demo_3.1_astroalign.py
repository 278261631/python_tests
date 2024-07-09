import matplotlib
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from astropy.wcs import WCS
import matplotlib.pyplot as plt
from reproject import reproject_interp
matplotlib.use('TkAgg')
import astroalign as aa

# hdu1 = fits.open(get_pkg_data_filename('src_process/test_/109120220506194824.fits'))[0]
# hdu2 = fits.open(get_pkg_data_filename('src_process/test_/209120220407205125.fits'))[0]


# 读取FITS文件
image1 = fits.open('src_process/test_/109120220506194824.fits')
image2 = fits.open('src_process/test_/209120220407205125.fits')

# 选择对齐方法，这里使用互相关
method = 'cross_correlation'

# 对齐图像
aligned_image, footprint = aa.register(image1[0].data, image2[0].data, detection_sigma=4)

# 保存或显示对齐后的图像
fits.writeto('src_process/test_/aligned_image1.fits', aligned_image)
