from astroscrappy import detect_cosmics
from astropy.io import fits
image = fits.open('E:/fix_data/2022/603520220828160816.fits')
image_data = image[0].data  # 假设数据在主扩展区
# 检测图像中的拖线
cleaned_image = detect_cosmics(image_data, gain=1.0, readnoise=5.0, sigclip=3.0)
