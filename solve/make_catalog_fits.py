from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from photutils import DAOStarFinder, apertures, AncillaryData
from astropy.table import Table, Column

# 读取FITS图像
image_path = r'E:/testimg/GY1_K040-6_No Filter_60S_Bin2_UTC20231010_200646_-19.9C_.fit'

with fits.open(image_path) as hdul:
    image_data = hdul[0].data  # 假设图像在HDU 0

# 估计背景和噪声
mean, median, std = sigma_clipped_stats(image_data, sigma=3.0)

# 使用DAOStarFinder检测源
daofind = DAOStarFinder(fwhm=3.0, threshold=5.0*std)
sources = daofind(image_data - mean)

# 创建一个源表
catalog = Table()
catalog['X_IMAGE'] = sources['xcentroid']
catalog['Y_IMAGE'] = sources['ycentroid']
catalog['FLUX'] = sources['flux']

# 保存源表为FITS文件
catalog.write('catalog.fits', overwrite=True)
