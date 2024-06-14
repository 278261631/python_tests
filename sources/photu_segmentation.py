
import os
import matplotlib
import numpy as np
from astropy import wcs
from astropy.convolution import convolve
from astropy.coordinates import SkyCoord
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.visualization import ImageNormalize, SqrtStretch
from matplotlib.patches import Circle
from photutils.aperture import CircularAperture, aperture_photometry
from photutils.background import MedianBackground, Background2D
from photutils.detection import DAOStarFinder
from photutils.segmentation import make_2dgaussian_kernel, detect_sources

matplotlib.use('TkAgg')

file_root = r'e:/src_process/10.500000_10.10000000_small/'
ra = 10.5
dec = 10.1
item_coord = SkyCoord(ra=ra, dec=dec, unit='deg')
files = os.listdir(file_root)

img_sub_x_wid = 400
img_sub_y_wid = 300

for file_index, file in enumerate(files):
    if file.endswith('.txt'):
        fits_id = file.replace('.txt', '')
        fits_file_name = f'{fits_id}.fits'
        png_file_name = f'{fits_id}.png'
        png_seg_file_name = f'{fits_id}_seg.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_seg_full_path = os.path.join(file_root, png_seg_file_name)
        txt_full_path = os.path.join(file_root, file)
        print(f'++ {fits_file_name}')
        with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
            line = txt_file.readline()
            wcs_info = wcs.WCS(line)
        print(f'{line}')
        print(f'{item_coord}')
        # pix_xy = wcs_info.world_to_pixel(item_coord)
        # print(f'pix:   {pix_xy}')

        hdu = fits.open(fits_full_path)

        data = hdu[0].data
        hdu.close()
        height, width = data.shape
        # data = data[1000:1300, 1000:1400]

        bkg_estimator = MedianBackground()
        bkg = Background2D(data, (50, 50), filter_size=(3, 3),
                           bkg_estimator=bkg_estimator)
        # data -= bkg.background  # subtract the background
        data = (data - bkg.background).astype(np.uint16)

        threshold = 1.5 * bkg.background_rms

        kernel = make_2dgaussian_kernel(3.0, size=5)  # FWHM = 3.0
        convolved_data = convolve(data, kernel)

        segment_map = detect_sources(convolved_data, threshold, npixels=10)
        print(segment_map)

        norm = ImageNormalize(stretch=SqrtStretch())
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12.5))
        ax1.imshow(data, origin='lower', cmap='Greys_r', norm=norm)
        ax1.set_title('Background-subtracted Data')
        ax2.imshow(segment_map, origin='lower', cmap=segment_map.cmap,
                   interpolation='nearest')
        ax2.set_title('Segmentation Image')
        plt.show()
        plt.savefig(png_seg_full_path, dpi=300, format='png', bbox_inches='tight')


        break




