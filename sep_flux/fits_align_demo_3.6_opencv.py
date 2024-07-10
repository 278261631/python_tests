import cv2
import numpy as np
from astropy.io import fits


def align_images(image_file1, image_file2):
    """
    对齐两个仅含有点源的图像，即使只有少部分重叠。

    Args:
        image_file1 (str): 第一个图像文件路径。
        image_file2 (str): 第二个图像文件路径。

    Returns:
        tuple: 包含两个对齐后的图像的元组 (aligned_image1, aligned_image2)。
    """

    # 加载图像
    image1 = cv2.imread(image_file1, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image_file2, cv2.IMREAD_GRAYSCALE)

    # 使用 SIFT 检测点源
    sift = cv2.SIFT_create()
    keypoints1, descriptors1 = sift.detectAndCompute(image1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(image2, None)
    # # 筛选出最大的 100 个点源
    keypoints1 = sorted(keypoints1, key=lambda x: x.response, reverse=True)[:100]
    keypoints2 = sorted(keypoints2, key=lambda x: x.response, reverse=True)[:100]

    # 特征匹配
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)

    # 使用 Lowe's Ratio Test 过滤匹配
    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    # 获取匹配点坐标
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    # 计算变换矩阵
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

    # 对齐图像
    aligned_image1 = cv2.warpPerspective(image1, M, (image2.shape[1], image2.shape[0]))
    aligned_image2 = image2

    # 在对齐后的图像上绘制点源
    image1_with_keypoints = cv2.drawKeypoints(aligned_image1, keypoints1, None, color=(0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    image2_with_keypoints = cv2.drawKeypoints(aligned_image2, keypoints2, None, color=(0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return image1_with_keypoints, image2_with_keypoints


# 示例用法
image_file1 = "src_process/test_/s_109120220407205235.png"
image_file2 = "src_process/test_/s_209120220407205125.png"
image1_with_keypoints, image2_with_keypoints = align_images(image_file1, image_file2)

# 显示结果
cv2.imshow("Aligned Image 1 with Keypoints", image1_with_keypoints)
cv2.imshow("Aligned Image 2 with Keypoints", image2_with_keypoints)
cv2.waitKey(0)
cv2.destroyAllWindows()