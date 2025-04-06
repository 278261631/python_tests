import numpy as np
from astropy.io import fits

# SLICE = f'E:/kats_process/GY1_K035-4_No Filter_60S_Bin2_UTC20240623_193150_-13.1C_.fit'
SLICE = f'E:/kats_process/GY1_K014-5_No Filter_60S_Bin2_UTC20250224_191818_-25C_.fit'
with fits.open(SLICE) as hdul:
    # 获取第一个HDU的数据（根据代码中的使用习惯）
    data = hdul[0].data.byteswap().newbyteorder()  # 处理字节顺序
    first_500_rows = data[:100]  # 处理一维情况

    # 禁用numpy的打印截断
    np.set_printoptions(threshold=np.inf, linewidth=np.inf)

    # 打印前500行（二维数据的情况）
    if len(data.shape) == 2:
        print("完整的前500行数据：")
        print(data[:500, :])  # 打印全部列

