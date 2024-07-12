import os
import random

import cv2
import matplotlib
import numpy as np
import sep

matplotlib.use('TkAgg')



import cv2
import numpy as np

def find_overlap_by_sep(img1_path, img2_path, output_path_img1="img1_keypoints.png", output_path_img2="img2_keypoints.png", output_path_overlap="overlap.png"):
    """
    使用 SEP 的 extract 查找重叠区域，并保存结果。

    参数
    ----------
    img1_path : str
        第一张图片的路径。
    img2_path : str
        第二张图片的路径。
    output_path_img1 : str, 可选
        标记了点状源的第一张图片保存的路径，默认值为 "img1_keypoints.png"。
    output_path_img2 : str, 可选
        标记了点状源的第二张图片保存的路径，默认值为 "img2_keypoints.png"。
    output_path_overlap : str, 可选
        重叠区域保存的路径，默认值为 "overlap.png"。

    返回值
    -------
    None
    """

    # 加载图片
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 使用 SEP 的 extract 检测点状源
    # 如果知道图像的噪声方差，使用 var 参数
    # objects1 = sep.extract(gray1, 1.5, 5, var=variance)  # 将 variance 替换为噪声方差

    # 如果不知道图像的噪声方差，使用 err 参数
    gray1 = gray1.astype(np.float32)
    gray2 = gray2.astype(np.float32)
    bkg_1 = sep.Background(gray1)
    gray1 = gray1 - bkg_1
    bkg_2 = sep.Background(gray2)
    gray2 = gray2 - bkg_2
    objects1_all = sep.extract(gray1, thresh=1.5, err=bkg_1.globalrms)
    objects2_all = sep.extract(gray2, thresh=1.5, err=bkg_2.globalrms)
    print(f'sources: [{len(objects1_all)}]    [{len(objects2_all)}]')
    objects1 = []
    for obj in objects1_all:
        if obj['flux'] > 5000 or obj['a'] > 100:
            objects1.append(obj)
    objects2 = []
    for obj in objects2_all:
        if obj['flux'] > 5000 or obj['a'] > 100:
            objects2.append(obj)

    print(f'sources: [{len(objects1)}]    [{len(objects2)}]')
    # 在两张图片上标记点状源
    img1_with_keypoints = img1.copy()
    img2_with_keypoints = img2.copy()
    for obj1 in objects1:
        cv2.circle(img1_with_keypoints, (int(obj1['x']), int(obj1['y'])), int(obj1['a']), (0, 255, 0), 2)
    for obj2 in objects2:
        cv2.circle(img2_with_keypoints, (int(obj2['x']), int(obj2['y'])), int(obj2['a']), (0, 255, 0), 2)

    # 比较点状源位置
    overlap_mask = np.zeros_like(gray1, dtype=np.uint8)
    # for obj1 in objects1:
    #     for obj2 in objects2:
    #         # 计算距离
    #         distance = np.sqrt((obj1['x'] - obj2['x'])**2 + (obj1['y'] - obj2['y'])**2)
    #         # 如果距离小于阈值，则认为是同一个点状源
    #         if distance < 5:
    #             cv2.circle(overlap_mask, (int(obj1['x']), int(obj1['y'])), int(obj1['a']), (255, 255, 255), -1)

    # # 随机选择200个点
    # random_indices_1 = random.sample(range(len(objects1)), 300)
    # selected_objects_1 = [objects2[i] for i in random_indices_1]
    # random_indices_2 = random.sample(range(len(objects2)), 300)
    # selected_objects_2 = [objects2[i] for i in random_indices_2]

    # 连接点的函数
    # 连接点的函数

    def connect_points(objects, img):
        dot_line_counter_i = 0
        for i, obj1 in enumerate(objects):
            dot_line_counter_i = 0
            dot_line_counter_j = 0
            for j, obj2 in enumerate(objects):
                dot_line_counter_j = 0
                if i != j:  # 不连接到自身
                    # 计算两点之间的距离
                    distance = np.sqrt((obj1['x'] - obj2['x']) ** 2 + (obj1['y'] - obj2['y']) ** 2)
                    if distance <= 200:  # 距离在100像素以内
                        # 连接点
                        cv2.line(img, (int(obj1['x']), int(obj1['y'])), (int(obj2['x']), int(obj2['y'])), (255, 255, 255), 3)
                        dot_line_counter_j = dot_line_counter_i+1
                        dot_line_counter_i = dot_line_counter_i+1
                if dot_line_counter_j > 4:
                    continue
            if dot_line_counter_i > 4:
                continue

    # 标记点状源并连接
    # img1_with_lines = img1.copy()
    img1_with_lines = np.zeros(img1.shape, dtype=np.uint8)
    for obj in objects1:
        # cv2.circle(img1_with_lines, (int(obj['x']), int(obj['y'])), int(obj['a']), (0, 255, 0), 2)
        cv2.circle(img1_with_lines, (int(obj['x']), int(obj['y'])), 50, (255, 255, 255), -1)
    # connect_points(objects1, img1_with_lines)

    # 保存图像
    cv2.imwrite('src_process/test_/p-lines-1.png', img1_with_lines)

    # 标记点状源并连接
    # img2_with_lines = img2.copy()
    img2_with_lines = np.zeros(img2.shape, dtype=np.uint8)
    for obj in objects2:
        # cv2.circle(img2_with_lines, (int(obj['x']), int(obj['y'])), int(obj['a']), (0, 255, 0), 2)
        cv2.circle(img2_with_lines, (int(obj['x']), int(obj['y'])), 50, (255, 255, 255), -1)
    # connect_points(objects2, img2_with_lines)

    # 保存图像
    cv2.imwrite('src_process/test_/p-lines-2.png', img2_with_lines)



    # 使用重叠区域掩码提取重叠部分
    overlap_region = img1 * np.expand_dims(overlap_mask, axis=-1)

    # 保存图片
    cv2.imwrite(output_path_img1, img1_with_keypoints)
    cv2.imwrite(output_path_img2, img2_with_keypoints)
    cv2.imwrite(output_path_overlap, overlap_region)


file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 's_109120220407205235.png')
png_2_path = os.path.join(file_root, 's_209120220407205125.png')
png_key_1_path = os.path.join(file_root, 'hough_key_1.png')
png_key_2_path = os.path.join(file_root, 'hough_key_2.png')
png_over_path = os.path.join(file_root, 'hough_.png')
# 加载图片
images = [cv2.imread(png_1_path), cv2.imread(png_2_path)]

# 拼接图片并保存
find_overlap_by_sep(png_1_path, png_2_path, png_key_1_path,png_key_2_path, png_over_path)


