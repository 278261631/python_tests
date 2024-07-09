import os

import matplotlib
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from astropy.wcs import WCS
import matplotlib.pyplot as plt
from reproject import reproject_interp
matplotlib.use('TkAgg')
import astroalign as aa
from fits_align.ident import make_transforms
from fits_align.align import affineremap
from glob import glob
from numpy import shape
import starsalign as sa
# hdu1 = fits.open(get_pkg_data_filename('src_process/test_/109120220506194824.fits'))[0]
# hdu2 = fits.open(get_pkg_data_filename('src_process/test_/209120220407205125.fits'))[0]


# 读取FITS文件
image1 = fits.open('src_process/test_/109120220506194824.fits')
image2 = fits.open('src_process/test_/209120220407205125.fits')


tmp_dir = 'src_process/test_/'

aligned_image = sa.fast_align(image1[0].data, image2[0].data)
fits.writeto('src_process/test_/aligned_image1.fits', aligned_image)

