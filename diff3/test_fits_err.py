import cv2
import numpy as np
from astropy.io import fits
from astropy.visualization import ImageNormalize, MinMaxInterval


fits_ok = f'../diff/GY1_K035-4_C_60S_Bin2_UTC20240623_193150_-13.1C__pp_ref_cut1.fits'
# fits_er = f'../diff2/GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp_ref_cut1.fits'
# fits_er = f'E:/kats_process/debug_zo2/K014/redux/GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp.fits'
# fits_er = f'E:/kats_process/debug_zo2/K014/redux/GY1_K014-5_C_60S_Bin2_UTC20250224_191818_-25C__pp_solved.fits'
fits_er = f'E:/kats_process/debug_zo2/K014/redux/GY1_K014-5_No Filter_60S_Bin2_UTC20250224_191818_-25C_.fit'

# 加载fits_ok fits_er并保存为jpg
fits_ok_jpg = f'ok.jpg'
fits_er_jpg = f'er.jpg'

# 读取fits文件
hdulist_ok = fits.open(fits_ok)
hdulist_er = fits.open(fits_er)


# 应用处理函数
image_ok = hdulist_ok[0].data
image_er = hdulist_er[0].data




print("NaN values:", np.isnan(image_ok).any())
print("Inf values:", np.isinf(image_ok).any())


print("NaN values:", np.isnan(image_er).any())
print("Inf values:", np.isinf(image_er).any())
print("Data range before:", np.nanmin(image_er), np.nanmax(image_er))
min_val = np.nanmin(image_er)
print("Replacing NaN with:", min_val)


# 在替换nan之前获取原始nan位置
nan_locations = np.where(np.isnan(image_er))
print("NaN positions (row, column):")
nan_counter = 0
for row, col in zip(*nan_locations):
    # print(f"({row}, {col})")
    nan_counter = nan_counter + 1
print(f'nan_counter:{nan_counter} in {image_er.shape}  {len(image_er)}')

image_er = np.nan_to_num(image_er, nan=min_val, posinf=255, neginf=0)
# image_er = np.nan_to_num(image_er, nan=0, posinf=255, neginf=0)
print("Data range after:", np.min(image_er), np.max(image_er))

norm_er = ImageNormalize(image_er, interval=MinMaxInterval())
image_er_normalized = norm_er(image_er).data * 255
image_er = np.uint8(image_er_normalized)

image_ok = np.uint8(image_ok)
image_er = np.uint8(image_er)

# 保存为jpg文件
cv2.imwrite(fits_ok_jpg, image_ok)
cv2.imwrite(fits_er_jpg, image_er)
