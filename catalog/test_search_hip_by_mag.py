from astropy.io import ascii
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.table import Table
# 假设你已经下载了HIP星表的数据文件，并保存为'hip_main.dat'，位于当前目录
# 加载星表数据
# hip_data = ascii.read(r'E:\catalog\hip2000-master/hip_main.dat')

hip_table = Table.read(r'E:\catalog\hip2000-master/hip_main.dat', format='ascii.fixed_width_no_header')

# 假设我们想要获取视星等小于等于8的恒星列表
magnitude_limit = 8

# 筛选星等小于等于8的恒星
# 假设HIP星表中的星等字段是 'Vmag'，您需要根据实际的星表结构进行调整
selected_stars = hip_table[hip_table['col6'] <= magnitude_limit]

# 输出筛选后的恒星列表
# for star in selected_stars:
#     print(star)

print(f'------{len(selected_stars)}')



# 打印恒星的坐标信息
# print(f"Coordinates for HIP {hip_number}: {star}     {star.ra.value}   {star.dec.value}")
