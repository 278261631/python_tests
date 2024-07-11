import os
import cv2
import matplotlib
import numpy as np

matplotlib.use('TkAgg')

file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 's_209120220407205125.png')
png_2_path = os.path.join(file_root, 's_109120220407205235.png')

image1 = cv2.imread(png_1_path)
image2 = cv2.imread(png_2_path)


gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

# 使用ORB特征检测器
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)


# 创建BFMatcher对象
matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# 匹配描述符
matches = matcher.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

# 使用RANSAC算法找到单应性矩阵
src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
H, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)



# 使用单应性矩阵变换图像
transformed_image2 = cv2.warpPerspective(image2, H, (image1.shape[1], image1.shape[0]))

# 找到重叠区域
mask = cv2.absdiff(transformed_image2, image1)
overlap = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
overlap = cv2.threshold(overlap, 1, 255, cv2.THRESH_BINARY)[1]

cv2.imshow('Overlap', overlap)
cv2.waitKey(0)
cv2.destroyAllWindows()

