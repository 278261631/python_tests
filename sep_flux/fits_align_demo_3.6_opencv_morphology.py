import os
import cv2
import matplotlib
import numpy as np

matplotlib.use('TkAgg')


import cv2
import numpy as np

def find_overlap_by_morphology(img1, img2):
    """
    使用形态学操作查找重叠区域。

    参数
    ----------
    img1 : numpy.ndarray
        第一张图片。
    img2 : numpy.ndarray
        第二张图片。

    返回值
    -------
    overlap_mask : numpy.ndarray
        重叠区域的掩码，值为1表示重叠，值为0表示不重叠。
    """

    # 二值化
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    ret1, thresh1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    ret2, thresh2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 膨胀
    kernel = np.ones((3, 3), np.uint8)
    thresh1 = cv2.dilate(thresh1, kernel, iterations=1)
    thresh2 = cv2.dilate(thresh2, kernel, iterations=1)

    # 腐蚀
    thresh1 = cv2.erode(thresh1, kernel, iterations=1)
    thresh2 = cv2.erode(thresh2, kernel, iterations=1)

    # 比较二值化图像
    overlap_mask = np.where(thresh1 == thresh2, 1, 0)

    return overlap_mask


file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 's_209120220407205125.png')
png_2_path = os.path.join(file_root, 's_109120220407205235.png')
png_over_path = os.path.join(file_root, 'morphology.png')
# 加载图片
img1 = cv2.imread(png_1_path)
img2 = cv2.imread(png_2_path)

# 查找重叠区域
overlap_mask = find_overlap_by_morphology(img1, img2)

# 使用重叠区域掩码提取重叠部分
gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
overlap_region = gray * overlap_mask
cv2.imwrite(png_over_path, overlap_region)

# # 显示重叠部分
# cv2.imshow('Overlap', overlap_region)
# cv2.waitKey(0)
# cv2.destroyAllWindows()





