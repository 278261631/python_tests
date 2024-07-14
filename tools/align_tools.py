import os

import cv2
import cv2 as cv
import numpy as np
import sep
from astropy.io import fits


def find_overlap_by_sep(img1_path, output_path_img_key, output_path_img_mark):
    # 加载图片
    img1 = cv2.imread(img1_path)
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    gray1 = gray1.astype(np.float32)
    bkg_1 = sep.Background(gray1)
    gray1 = gray1 - bkg_1
    objects1_all = sep.extract(gray1, thresh=1.5, err=bkg_1.globalrms)
    objects1_all = sorted(objects1_all, key=lambda s_obj: s_obj['flux'], reverse=True)

    print(f'sources: [{len(objects1_all)}]   [{objects1_all[0]["flux"]}]  [{objects1_all[0]["a"]}]')
    objects1 = []

    for obj_idx, obj in enumerate(objects1_all):
        if obj_idx < 500:
            objects1.append(obj)
    # for obj in objects1_all:
    #     if obj['flux'] > 5000 or obj['a'] > 100:
    #         objects1.append(obj)

    img1_with_keypoints = img1.copy()
    for obj1 in objects1:
        cv2.circle(img1_with_keypoints, (int(obj1['x']), int(obj1['y'])), int(obj1['a']), (0, 255, 0), 2)
    img1_with_lines = np.zeros(img1.shape, dtype=np.uint8)
    for obj in objects1:
        # cv2.circle(img1_with_lines, (int(obj['x']), int(obj['y'])), int(obj['a']), (0, 255, 0), 2)
        cv2.circle(img1_with_lines, (int(obj['x']), int(obj['y'])), 50, (255, 255, 255), -1)
    # connect_points(objects1, img1_with_lines)

    # 保存图像
    cv2.imwrite(output_path_img_mark, img1_with_lines)

    cv2.imwrite(output_path_img_key, img1_with_keypoints)


def align_fits_by_light_stars(fits_1_path, fits_2_path, png_1_path, png_2_path, fits_transformed_path, png_over_path,
                              png_trans_debug):
    with fits.open(fits_1_path) as hdul1:
        img1_data = hdul1[0].data

    with fits.open(fits_2_path) as hdul2:
        img2_data = hdul2[0].data

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

        # 获取img2的尺寸
        h, w = img2.shape

        # 创建一个与img2相同尺寸的点集，用于应用单应性变换
        points2D = np.float32([[x, y] for y in range(h) for x in range(w)]).reshape(-1, 1, 2)

        # 步骤1: 使用单应性矩阵变换img2中的所有点
        transformed_pts = cv.perspectiveTransform(points2D, M)

        # 创建一个新的图像，尺寸与img1相同
        transformed_img2 = cv.warpPerspective(img1, M, (w, h))

        transformed_img2_fits = cv.warpPerspective(img1_data, M, (w, h))

        # 步骤2: 保存变换后的图像
        cv.imwrite(png_trans_debug, transformed_img2)

        hdu = fits.PrimaryHDU(transformed_img2_fits)
        hdul = fits.HDUList([hdu])
        hdul.writeto(fits_transformed_path, overwrite=True)

    else:
        print("Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT))
        matchesMask = None

    draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                       singlePointColor=None,
                       matchesMask=matchesMask,  # draw only inliers
                       flags=2)

    img3 = cv.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

    cv.imwrite(png_over_path, img3)
