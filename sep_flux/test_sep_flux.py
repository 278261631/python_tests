import matplotlib
import matplotlib.pyplot as plt
import sep
from astropy.io import fits
from astropy.nddata import Cutout2D
from skimage import color, morphology
from skimage.util import img_as_float
matplotlib.use('TkAgg')


# 读取FITS文件
fits_file = f'sub_fits.fits'
with fits.open(fits_file) as hdul:
    image_FITS = hdul[0].data  # 假设数据存储在HDU 0中

# 将16位数据转换为浮点格式
image_fits = img_as_float(image_FITS)

# 使用SEP进行源检测
bkg = sep.Background(image_fits)
bkg_image = bkg.back()
objects = sep.extract(image_fits-bkg_image, 1.5, err=bkg.globalrms)

fields = objects.dtype.names
print(fields)
for idx, item in enumerate(objects):
    # print(f'{idx}  {item}')
    pass


image_shape = image_fits.shape
# 准备绘制图像
fig, ax = plt.subplots()
# fig.set_size_inches(image_fits.shape[1], image_fits.shape[0])


# 在图像上为每个源绘制圆圈
for obj in objects:
    # 圆圈的中心位置
    center_x = obj['x']
    center_y = obj['y']
    # 圆圈的半径，这里使用a参数的一半作为圆圈半径
    radius = obj['a'] * 4.0
    # 绘制圆圈
    circle = plt.Circle((center_x, center_y), radius, color='red', fill=False, linewidth=0.2)
    ax.add_patch(circle)


ax.axis('off')
ax.imshow(image_fits, cmap='gray')
# 保存绘制了圆圈的图像
plt.savefig('sub_fits_with_circles.png', bbox_inches='tight', pad_inches=0, dpi=200)
plt.close(fig)

# 保存新的FITS文件
hdu = fits.PrimaryHDU(image_fits, header=hdul[0].header)
hdulist = fits.HDUList([hdu])
hdulist.writeto('sub_fits_with_sources.fits', overwrite=True)

# 保存新的FITS文件
hdu_m_bg = fits.PrimaryHDU(image_fits-bkg_image, header=hdul[0].header)
hdulist_mbg = fits.HDUList([hdu_m_bg])
hdulist_mbg.writeto('sub_fits_mbg.fits', overwrite=True)

