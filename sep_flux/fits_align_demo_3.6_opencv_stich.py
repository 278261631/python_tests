import os
import cv2
import matplotlib
import numpy as np

matplotlib.use('TkAgg')



import cv2
import numpy as np


def stitch_images(images, output_path="panorama.png"):
    """
    拼接多张图片，并在第一张图片上标记重叠区域，并将拼接后的全景图像保存。

    参数
    ----------
    images : list of numpy.ndarray
        待拼接的图片列表。
    output_path : str, 可选
        拼接后的全景图像保存的路径，默认值为 "panorama.png"。

    返回值
    -------
    None
    """

    # 1. 特征点检测与匹配
    keypoints = []
    descriptors = []
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create()
        kp, des = orb.detectAndCompute(gray, None)
        keypoints.append(kp)
        descriptors.append(des)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors[0], descriptors[1])
    matches = sorted(matches, key=lambda x: x.distance)

    # 2. 几何变换计算
    src_pts = np.float32([keypoints[0][m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints[1][m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # 3. 图像融合
    h, w = images[0].shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    # 找到重叠区域
    x_min = int(min(dst[:, 0, 0]))
    x_max = int(max(dst[:, 0, 0]))
    y_min = int(min(dst[:, 0, 1]))
    y_max = int(max(dst[:, 0, 1]))

    # 在第一张图片上标记重叠区域
    images[0] = cv2.rectangle(images[0], (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

    # 创建拼接后的图像
    panorama = cv2.warpPerspective(images[0], M, (images[1].shape[1] + images[0].shape[1], images[1].shape[0]))
    panorama[0:images[1].shape[0], 0:images[1].shape[1]] = images[1]

    # 保存图片
    cv2.imwrite(output_path, panorama)


file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 's_209120220407205125.png')
png_2_path = os.path.join(file_root, 's_109120220407205235.png')
png_over_path = os.path.join(file_root, 'stich_.png')
# 加载图片
images = [cv2.imread(png_1_path), cv2.imread(png_2_path)]

# 拼接图片并保存
stitch_images(images, png_over_path)


