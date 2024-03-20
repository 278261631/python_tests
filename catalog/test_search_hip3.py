from astropy.io import ascii
from astropy.coordinates import SkyCoord
import astropy.units as u

# 假设你已经下载了HIP星表的数据文件，并保存为'hip_main.dat'，位于当前目录
# 加载星表数据
hip_data = ascii.read(r'E:\catalog\hip2000-master/hip_main.dat')


# 定义一个函数来查询特定HIP编号的恒星
def query_hip(hip_id):
    # 使用SkyCoord来查询恒星的坐标
    # 这里我们假设hip_data表中有一个名为'HIP'的列，包含HIP编号
    star = SkyCoord(hip_data[hip_data['col2'] == hip_id]['col4'].data[0],
                    hip_data[hip_data['col2'] == hip_id]['col5'].data[0],
                    unit=(u.hour, u.degree),
                    frame='icrs')
    return star


# 查询HIP 67301的恒星
hip_number = 67301
star = query_hip(hip_number)

# 打印恒星的坐标信息
print(f"Coordinates for HIP {hip_number}: {star}     {star.ra.value}   {star.dec.value}")
