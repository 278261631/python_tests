import matplotlib
import numpy as np
from astropy.io import fits

matplotlib.use('Agg')  # 在导入pyplot之前设置非交互式后端
import matplotlib.pyplot as plt


# 读取FITS文件
filename = 'GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.diff1.fits'
with fits.open(filename) as hdul:
    data = hdul[0].data  # 获取第一个HDU的数据

fig = plt.figure(figsize=(data.shape[1]/100, data.shape[0]/100), dpi=100)  # 假设原始数据尺寸为HxW

# 2. 显示时关闭坐标轴自动调整
ax = fig.add_axes([0, 0, 1, 1])  # [左，底，宽，高] 占满整个画布
ax.imshow(data,
          cmap='gray',
          origin='lower',
          aspect='equal',  # 保持像素等比例
          interpolation='none')  # 禁用插值

# 3. 关闭坐标轴显示
ax.axis('off')

# 4. 保存时指定精确参数
plt.savefig('diff_image.png',
           bbox_inches='tight',
           pad_inches=0,
           dpi=100)  # 保持与figsize的dpi一致

#
# # 显示图像
# plt.figure(figsize=(10, 8))
# plt.imshow(data,
#            cmap='gray',
#            origin='lower',
#            vmin=np.percentile(data, 5),   # 自动对比度拉伸
#            vmax=np.percentile(data, 95)
#            )
# plt.colorbar(label='Intensity')
# plt.title(f'FITS Image: {filename}')
# plt.xlabel('X Pixel')
# plt.ylabel('Y Pixel')
#
#
# plt.savefig('diff_image.png', bbox_inches='tight')
# plt.close()


