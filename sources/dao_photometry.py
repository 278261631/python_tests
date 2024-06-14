
import os
import matplotlib
import numpy as np
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy.io import fits
import matplotlib.pyplot as plt
from astropy.visualization import ImageNormalize, SqrtStretch
from matplotlib.patches import Circle
from photutils.aperture import CircularAperture, aperture_photometry
from photutils.detection import DAOStarFinder

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
        png_photo_file_name = f'{fits_id}_photo.png'
        fits_full_path = os.path.join(file_root, fits_file_name)
        png_photo_full_path = os.path.join(file_root, png_photo_file_name)
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

        star_finder = DAOStarFinder(fwhm=30.0, threshold=50.0)
        sources = star_finder(data)
        print(sources[0])
        print(f'----------------')
        # 定义一个光圈，例如5x5像素
        # positions = sources['positions']
        positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
        print(len(positions))
        print(f'----------------')
        apertures = CircularAperture(positions, r=4.0)
        phot_table = aperture_photometry(data, apertures)
        print(phot_table)

        norm = ImageNormalize(stretch=SqrtStretch())
        plt.imshow(data, cmap='Greys', origin='lower', norm=norm, interpolation='nearest')
        apertures.plot(color='blue', lw=1.5, alpha=0.5)
        plt.savefig(png_photo_full_path, dpi=300, format='png', bbox_inches='tight')
        plt.show()
        break




