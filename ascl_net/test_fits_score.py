import numpy as np
from astropy.io import fits

def jpeg_quality_score(img):
    # 检查输入参数数量
    if img.ndim != 2 or img.dtype != np.uint16:
        return -1

    [M, N] = img.shape
    if M < 16 or N < 16:
        return -2

    # 将16位图像数据转换为浮点数
    x = img.astype(np.float64)

    # 特征提取函数
    def feature_extraction(x, axis):
        d = np.diff(x, axis=axis)
        B = np.mean(np.abs(d))
        A = np.mean(d != 0)
        Z = np.mean(np.diff(np.sign(d)) != 0)
        return B, A, Z

    B_h, A_h, Z_h = feature_extraction(x, 1)
    B_v, A_v, Z_v = feature_extraction(x, 0)

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
    score = alpha + beta * (B ** gamma1) * (A ** gamma2) * (Z ** gamma3)

    return score

def load_fits_and_calculate_score(fits_file_path):
    # 从FITS文件读取图像数据
    with fits.open(fits_file_path) as hdul:
        img = hdul[0].data  # 假设第一张HDU包含图像数据

    # 计算JPEG质量得分
    quality_score = jpeg_quality_score(img)
    return quality_score

# 使用示例
# fits_file_path = 'path_to_your_fits_file.fits'
# quality_score = load_fits_and_calculate_score(fits_file_path)
# print(f"The JPEG quality score is: {quality_score}")