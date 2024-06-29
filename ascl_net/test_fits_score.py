import os

from PIL import Image
import numpy as np
from astropy.io import fits


def jpeg_quality_score(img_path):
    # 从文件加载JPEG图像
    try:
        with fits.open(img_path) as hdul:
            # 假设FITS文件的第一个HDU包含我们想要的图像数据
            img = hdul[0].data
    except IOError as e:
        print(f"无法加载FITS文件：{e}")
        return -1

    # 将图像转换为numpy数组
    img_array = np.array(img)

    # # 检查输入参数数量和数据类型
    # if img_array.ndim != 2 or img_array.dtype != np.uint8:
    #     return -1

    [M, N] = img_array.shape
    if M < 16 or N < 16:
        return -2

    x = img_array.astype(np.double)

    # 特征提取
    def feature_extraction(x, axis):
        d = np.diff(x, axis=axis)
        # 检查切片是否有效
        if d.shape[axis] < 16:  # 确保至少有16个像素用于计算
            return 0, 0, 0  # 如果图像太小，返回0作为特征值

        # 计算B值
        center_start = d.shape[axis] // 2 - 8  # 从中心开始减去8
        center_end = center_start + 16  # 确保至少取16个像素
        B_slice = d[center_start:center_end]  # 直接使用切片操作符
        B = np.mean(np.abs(B_slice))

        # 计算A值
        A = (8 * np.mean(np.abs(d)) - B) / 7

        # 计算Z值，确保切片不为空
        sig = np.sign(d)
        if axis == 0:
            Z_slice = (sig[1:, :] * sig[:-1, :])
        else:
            Z_slice = (sig[:-1, :] * sig[1:, :])
        if Z_slice.size > 0:
            Z = np.mean(Z_slice < 0)
        else:
            Z = 0  # 如果Z_slice为空，设置Z为0

        return B, A, Z

    B_h, A_h, Z_h = feature_extraction(x, 0)  # 对于灰度图像，使用0轴提取水平特征
    B_v, A_v, Z_v = feature_extraction(x, 1)  # 使用1轴提取垂直特征

    # 组合特征
    B = (B_h + B_v) / 2
    A = (A_h + A_v) / 2
    Z = (Z_h + Z_v) / 2

    # 质量预测
    alpha = -927.4240
    beta = 850.8986
    gamma1 = 235.4451
    gamma2 = 128.7548
    gamma3 = -341.4790
    score = alpha + beta * (B ** (gamma1 / 10000)) * (A ** (gamma2 / 10000)) * (Z ** (gamma3 / 10000))

    return score


temp_fits_path = 'e:/fix_data/'
scores_list = []
files = os.listdir(temp_fits_path)

for file_index, file in enumerate(files):
    if file.endswith('.fits'):
        fits_full_path = os.path.join(temp_fits_path, file)
        quality_score = jpeg_quality_score(fits_full_path)
        print(f"FITS文件质量评分：{quality_score}  {file}")
        scores_list.append((file, quality_score))

print(f'=======================')
sorted_scores = sorted(scores_list, key=lambda x: x[1], reverse=True)
for file, score in sorted_scores:
    print(f"JPEG质量评分：{score}  {file}")

