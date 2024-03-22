from astropy.table import Table
from astroquery.astrometry_net import AstrometryNet

# 初始化AstrometryNet对象
ast = AstrometryNet()

# 设置你的API密钥，这里用'XXXXXXXXXXXXXXXX'代替你的实际API密钥
ast.api_key = 'XXXXXXXXXXXXXXXX'

# 读取包含源列表的FITS文件，这里用'catalog.fits'作为文件名
sources = Table.read('catalog.fits')

# 按亮度（FLUX）降序排序源列表
sources.sort('FLUX')
sources.reverse()

# 图像的宽度和高度
image_width = 3073
image_height = 2048

# 调用solve_from_source_list方法来求解WCS解决方案
wcs_header = ast.solve_from_source_list(sources['X_IMAGE'], sources['Y_IMAGE'],
                                        image_width, image_height, solve_timeout=120)

# 检查是否成功获取WCS解决方案
if wcs_header:
    # 如果成功，wcs_header将是一个包含WCS信息的astropy.io.fits.Header对象
    print(wcs_header)
else:
    # 如果失败，wcs_header将是一个空字典
    print("No solution found.")

# 你可以根据获取到的WCS头部信息进行后续的天文数据分析