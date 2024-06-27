import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

from skimage import measure
from skimage.util import img_as_float

# 读取FITS文件
fits_file = f'sub_fits.fits'
with fits.open(fits_file) as hdul:
    image_FITS = hdul[0].data  # 假设数据存储在HDU 0中

# 将16位数据转换为浮点格式
image_fits = img_as_float(image_FITS)
# Find contours at a constant value of 0.8
contours = measure.find_contours(image_fits, 0.9)
# edges1 = edges1.astype(np.int16) * 255

# contours_p = fits.PrimaryHDU(contours)
# hdu_contours = fits.HDUList(contours_p)
#
# contours_fits_file = 'contours.fits'
# hdu_contours.writeto(contours_fits_file, overwrite=True)
# print(f' {contours_fits_file}')

# Display the image and plot all contours found
fig, ax = plt.subplots()
ax.imshow(image_fits, cmap=plt.cm.gray)

for contour in contours:
    ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

ax.axis('image')
ax.set_xticks([])
ax.set_yticks([])
plt.show()

