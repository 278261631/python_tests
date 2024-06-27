import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from skimage.util import random_noise, img_as_float
from skimage import feature


# 读取FITS文件
fits_file = f'sub_fits.fits'
with fits.open(fits_file) as hdul:
    image_FITS = hdul[0].data  # 假设数据存储在HDU 0中

# 将16位数据转换为浮点格式
image_fits = img_as_float(image_FITS)

# Compute the Canny filter for two values of sigma
edges1 = feature.canny(image_fits)
edges2 = feature.canny(image_fits, sigma=3)

edges1 = edges1.astype(np.int16) * 255
edges2 = edges2.astype(np.int16) * 255

hdu_edges1_p = fits.PrimaryHDU(edges1)
hdu_edges1 = fits.HDUList(hdu_edges1_p)

hdu_edges2_p = fits.PrimaryHDU(edges2)
hdu_edges2 = fits.HDUList(hdu_edges2_p)

canny_e1_fits_file = 'canny_edges1.fits'
hdu_edges1.writeto(canny_e1_fits_file, overwrite=True)
print(f' {canny_e1_fits_file}')

canny_e2_fits_file = 'canny_edges2.fits'
hdu_edges2.writeto(canny_e2_fits_file, overwrite=True)
print(f' {canny_e2_fits_file}')


# display results
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(8, 3))

ax[0].imshow(image_fits, cmap='gray')
ax[0].set_title('noisy image', fontsize=20)

ax[1].imshow(edges1, cmap='gray')
ax[1].set_title(r'Canny filter, $\sigma=1$', fontsize=20)

ax[2].imshow(edges2, cmap='gray')
ax[2].set_title(r'Canny filter, $\sigma=3$', fontsize=20)

for a in ax:
    a.axis('off')

fig.tight_layout()
plt.show()

