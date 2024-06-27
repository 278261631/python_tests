import matplotlib.pyplot as plt
from astropy.io import fits
from skimage import color, morphology
from skimage.util import img_as_float


# 读取FITS文件
fits_file = f'sub_fits.fits'
with fits.open(fits_file) as hdul:
    image_FITS = hdul[0].data  # 假设数据存储在HDU 0中

# 将16位数据转换为浮点格式
image_fits = img_as_float(image_FITS)

footprint = morphology.disk(1)
res = morphology.white_tophat(image_fits, footprint)
hat_result = image_fits - res

hdu_w_hat_p = fits.PrimaryHDU(res)
hdu_w_hat = fits.HDUList(hdu_w_hat_p)

hdu_w_hat_r_p = fits.PrimaryHDU(hat_result)
hdu_w_hat_r = fits.HDUList(hdu_w_hat_r_p)

w_hat_fits_file = 'w_hat.fits'
hdu_w_hat.writeto(w_hat_fits_file, overwrite=True)
print(f' {w_hat_fits_file}')

w_hat_r_fits_file = 'w_hat_r.fits'
hdu_w_hat_r.writeto(w_hat_r_fits_file, overwrite=True)
print(f' {w_hat_r_fits_file}')


fig, ax = plt.subplots(ncols=3, figsize=(20, 8))
ax[0].set_title('Original')
ax[0].imshow(image_fits, cmap='gray')
ax[1].set_title('White tophat')
ax[1].imshow(res, cmap='gray')
ax[2].set_title('Complementary')
ax[2].imshow(image_fits - res, cmap='gray')

plt.show()
