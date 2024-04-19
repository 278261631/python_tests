from astropy.io import fits
from astropy.wcs import WCS, wcs

# 假设你已经有了一个FITS文件的路径
fits_file_path = r'E:\test_download\astap\6378.wcs'

# wcs = WCS.read(fits_file_path)
# wcs = fits.read_wcs(fits_file_path)
# with fits.open(fits_file_path) as fits_hdul:
#     hdul = fits_hdul
#     image_data = hdul[0].data

# header = fits.getheader(fits_file_path)

# with open(fits_file_path, 'r') as file:
#     wcs_header_str = file.read()
#
# print(wcs_header_str)
# wcs_info = WCS(wcs_header_str, naxis=2)
# print(wcs)


# 读取文本文件并解析每一行以提取头信息
header_dict = {}
with open(fits_file_path, 'r') as file:
    for line in file:
        line = line.strip()  # 去除行首尾的空白字符
        if line and not line.startswith('END') and '=' in line:
            if '/' in line:
                comment_index = line.index('/')
                line = line[:comment_index]
            line = line.replace("'", "")
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # 尝试将值转换为适当的数据类型
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                # 如果转换失败，保留原始字符串值
                pass

            header_dict[key] = value

# 使用字典创建WCS对象
wcs_info = WCS(header_dict)

print('-----------------')
print(wcs_info.wcs.crval)
print(wcs_info.wcs.crpix)
# print(wcs_info.wcs.cd)
print('-----------------')

ra_1, dec_1 = wcs_info.wcs_pix2world(0, 0, 1)
ra_2, dec_2 = wcs_info.wcs_pix2world(4799, 0, 1)
ra_3, dec_3 = wcs_info.wcs_pix2world(4799, 3210, 1)
ra_4, dec_4 = wcs_info.wcs_pix2world(3210, 0, 1)
print(f'{ra_1}   {dec_1}')
print(f'{ra_2}   {dec_2}')
print(f'{ra_3}   {dec_3}')
print(f'{ra_4}   {dec_4}')

x1, y1 = wcs_info.wcs_world2pix(ra_1, dec_1, 1)
x2, y2 = wcs_info.wcs_world2pix(ra_2, dec_2, 1)
x3, y3 = wcs_info.wcs_world2pix(ra_3, dec_3, 1)
x4, y4 = wcs_info.wcs_world2pix(ra_4, dec_4, 1)

print(f'{x1}   {y1}')
print(f'{x2}   {y2}')
print(f'{x3}   {y3}')
print(f'{x4}   {y4}')

