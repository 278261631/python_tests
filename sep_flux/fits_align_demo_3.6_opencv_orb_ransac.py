import os
import cv2
import matplotlib
import numpy as np

matplotlib.use('TkAgg')



import cv2
import numpy as np

def find_overlap(img1_path, img2_path, output_path_img1="img1_keypoints.png", output_path_img2="img2_keypoints.png", output_path_overlap="overlap.png"):
    """
    找到两张图片的重叠部分，并在原始图上标记特征点和重叠区域，并保存。

    参数
    ----------
    img1_path : str
        第一张图片的路径。
    img2_path : str
        第二张图片的路径。
    output_path_img1 : str, 可选
        标记了特征点的第一张图片保存的路径，默认值为 "img1_keypoints.png"。
    output_path_img2 : str, 可选
        标记了特征点的第二张图片保存的路径，默认值为 "img2_keypoints.png"。
    output_path_overlap : str, 可选
        重叠部分保存的路径，默认值为 "overlap.png"。

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

    # 使用ORB算法检测特征点
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    # 使用Brute-Force匹配器匹配特征点
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # 筛选好的匹配
    matches = sorted(matches, key=lambda x: x.distance)

    # 获取匹配的特征点坐标
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # 使用RANSAC计算变换矩阵
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # 将第一张图片投影到第二张图片上
    h, w = img1.shape[:2]
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    # 找到重叠区域
    x_min = int(min(dst[:, 0, 0]))
    x_max = int(max(dst[:, 0, 0]))
    y_min = int(min(dst[:, 0, 1]))
    y_max = int(max(dst[:, 0, 1]))
    overlap = img2[y_min:y_max, x_min:x_max]

    # 在两张图片上标记特征点
    img1_with_keypoints = cv2.drawKeypoints(img1, kp1, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    img2_with_keypoints = cv2.drawKeypoints(img2, kp2, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # 在第二张图片上标记重叠区域
    cv2.rectangle(img2_with_keypoints, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

    # 保存图片
    cv2.imwrite(output_path_img1, img1_with_keypoints)
    cv2.imwrite(output_path_img2, img2_with_keypoints)
    cv2.imwrite(output_path_overlap, overlap)


file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 's_209120220407205125.png')
png_2_path = os.path.join(file_root, 's_109120220407205235.png')
png_key_1_path = os.path.join(file_root, 'orb_key_1.png')
png_key_2_path = os.path.join(file_root, 'orb_key_2.png')
png_over_path = os.path.join(file_root, 'orb_over.png')

# 找出重叠部分
find_overlap(png_1_path, png_2_path, png_key_1_path, png_key_2_path, png_over_path)


# 显示重叠部分
# cv2.imshow('Overlap', overlap)
# cv2.waitKey(0)
# cv2.destroyAllWindows()



