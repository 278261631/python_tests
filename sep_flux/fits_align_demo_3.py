import matplotlib
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from astropy.wcs import WCS
import matplotlib.pyplot as plt
from reproject import reproject_interp, reproject_exact

matplotlib.use('TkAgg')

hdu1 = fits.open(get_pkg_data_filename('src_process/test_/109120220506194824.fits'))[0]
hdu2 = fits.open(get_pkg_data_filename('src_process/test_/209120220407205125.fits'))[0]

# #  fixme need astropy 5.*
# ax1 = plt.subplot(1, 2, 1, projection=WCS(hdu1.header))
# ax1.imshow(hdu1.data, origin='lower', vmin=-100., vmax=2000.)
# ax1.coords['ra'].set_axislabel('Right Ascension')
# ax1.coords['dec'].set_axislabel('Declination')
# ax1.set_title('2MASS K-band')
#
# #  fixme need astropy 5.*
# ax2 = plt.subplot(1, 2, 2, projection=WCS(hdu2.header))
# ax2.imshow(hdu2.data, origin='lower', vmin=-2.e-4, vmax=5.e-4)
# # ax2.coords['glon'].set_axislabel('Galactic Longitude')
# # ax2.coords['glat'].set_axislabel('Galactic Latitude')
# # ax2.coords['glat'].set_axislabel_position('r')
# # ax2.coords['glat'].set_ticklabel_position('r')
# ax2.set_title('MSX band E')


array, footprint = reproject_interp(hdu2, hdu1.header)
fits.writeto('src_process/test_/msx_on_2mass_header_21.fits', array, hdu1.header, overwrite=True)
# array, footprint = reproject_interp(hdu2, hdu1.header, order='bicubic')
# array, footprint = reproject_exact(hdu2, hdu1.header)

# array, footprint = reproject_interp(hdu1, hdu1.header)
# fits.writeto('src_process/test_/msx_on_2mass_header_11.fits', array, hdu1.header, overwrite=True)
