import os
import cv2 as cv
import matplotlib
import numpy as np
from matplotlib import pyplot as plt

matplotlib.use('TkAgg')


file_root = f'src_process/test_/'
png_1_path = os.path.join(file_root, 'p-lines-1.jpg')
png_2_path = os.path.join(file_root, 'p-lines-2.jpg')
png_key_1_path = os.path.join(file_root, 'doc_sift_key_1.png')
png_key_2_path = os.path.join(file_root, 'doc_sift_key_2.png')
png_over_path = os.path.join(file_root, 'doc_sift_over.png')

img1 = cv.imread(png_1_path, cv.IMREAD_GRAYSCALE)
img2 = cv.imread(png_2_path, cv.IMREAD_GRAYSCALE)


MIN_MATCH_COUNT = 10
# Initiate SIFT detector
sift = cv.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)

flann = cv.FlannBasedMatcher(index_params, search_params)

matches = flann.knnMatch(des1, des2, k=2)

# store all the good matches as per Lowe's ratio test.
good = []
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good.append(m)

if len(good) > MIN_MATCH_COUNT:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()

    h, w = img1.shape
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv.perspectiveTransform(pts, M)

    img2 = cv.polylines(img2, [np.int32(dst)], True, 255, 3, cv.LINE_AA)

else:
    print("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
    matchesMask = None

draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                   singlePointColor=None,
                   matchesMask=matchesMask,  # draw only inliers
                   flags=2)

img3 = cv.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

# plt.imshow(img3, 'gray'), plt.show()


# plt.imshow(img3), plt.show()

cv.imwrite(png_over_path, img3)


