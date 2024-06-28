import numpy as np
from scipy.ndimage import gaussian_filter


def jpeg_quality_score(img):
    # 版权和使用说明的注释（略）

    # 检查输入参数数量
    if img.ndim != 2 or img.dtype != np.uint8:
        return -1

    [M, N] = img.shape
    if M < 16 or N < 16:
        return -2

    x = img.astype(np.double)

    # 特征提取
    def feature_extraction(x, axis):
        d = np.diff(x, axis=axis)
        B = np.mean(np.abs(d[:, N//8*(N//8):N//8*(N//8+1)]))
        A = (8 * np.mean(np.abs(d)) - B) / 7
        sig = np.sign(d)
        if axis == 0:
            Z = np.mean((sig[1:, :] * sig[:-1, :]) < 0)
        else:
            Z = np.mean((sig[1:, :] * sig[:-1, :]) < 0)
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
    score = alpha + beta * (B ** (gamma1 / 10000)) * (A ** (gamma2 / 10000)) * (Z ** (gamma3 / 10000))

    return score

# 使用示例
# img = np.array(...)  # 加载或创建一个8位像素的灰度图像
# quality_score = jpeg_quality_score(img)