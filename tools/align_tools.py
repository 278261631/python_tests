import cv2
import numpy as np
import sep


def find_overlap_by_sep(img1_path, output_path_img_key, output_path_img_mark):

    # 加载图片
    img1 = cv2.imread(img1_path)
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

    gray1 = gray1.astype(np.float32)
    bkg_1 = sep.Background(gray1)
    gray1 = gray1 - bkg_1
    objects1_all = sep.extract(gray1, thresh=1.5, err=bkg_1.globalrms)
    print(f'sources: [{len(objects1_all)}]')
    objects1 = []
    for obj in objects1_all:
        if obj['flux'] > 5000 or obj['a'] > 100:
            objects1.append(obj)

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
