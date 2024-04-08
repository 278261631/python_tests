from astropy.io import fits
from astrometry.net import solve_from_source

# FITS 文件路径
fits_file = "path/to/your/file.fits"

# 读取 FITS 文件
with fits.open(fits_file) as hdul:
    data = hdul[0].data

# 对图像进行求解
try:
    wcs = solve_from_source(data, downsample_factor=2)
except Exception as e:
    print(f"板块求解过程中出现错误: {e}")
    exit(1)

# 打印求解后的 WCS 信息
print(f"WCS: {wcs}")

# 现在您可以使用 WCS 信息进行进一步的分析，
# 例如坐标转换或目标识别。