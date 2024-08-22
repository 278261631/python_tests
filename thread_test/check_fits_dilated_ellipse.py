import os
import shutil

import cv2
import matplotlib
import numpy as np
import sep
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle
from photutils.detection import DAOStarFinder
from skimage.color import rgb2gray


matplotlib.use('TkAgg')
from skimage import io, filters, measure, color, morphology, exposure, feature

sigma = 10
if __name__ == '__main__':
    temp_txt_path = 'e:/fix_data/2023/'
    copy_err_path = 'e:/fix_data/copy_err/'
    copy_ok_path = 'e:/fix_data/copy_ok/'
    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        fits_id = os.path.basename(file).replace('.fits', '')
        if file.endswith('.fits'):
            fits_full_path = os.path.join(temp_txt_path, file)
            png_err_full_path = os.path.join(copy_err_path, f'{fits_id}.png')
            png_ok_full_path = os.path.join(copy_ok_path, f'{fits_id}.png')
            copy_err_full_path = os.path.join(copy_err_path, f'{fits_id}.fits')
            copy_ok_full_path = os.path.join(copy_ok_path, f'{fits_id}.fits')
            print(f'{file_index}    {file} / {len(files)}')
            if os.path.exists(png_ok_full_path) or os.path.exists(png_err_full_path):
                print(f'skip  {file}')
                continue
            try:
                with fits.open(fits_full_path) as hdul:
                    image_data = hdul[0].data
            except Exception as e:
                continue

            # min_val = np.min(image_data)
            # max_val = np.max(image_data)
            #
            # # 线性映射到8位范围
            # if max_val > min_val:  # 防止除以0
            #     stretched_image = cv2.convertScaleAbs(image_data, alpha=(255.0 / (max_val - min_val)),
            #                                           beta=-(min_val * 255.0 / (max_val - min_val)))
            # else:
            #     # 如果所有像素值都相同，直接映射到128
            #     stretched_image = np.full_like(image_data, 128, dtype=np.uint8)

            # 计算直方图
            hist = cv2.calcHist([image_data], [0], None, [65536], [0, 65535])

            # 计算累积分布函数（CDF）
            cdf = hist.cumsum()
            cdf = cdf / cdf[-1]  # 归一化

            # 选择截止点，例如1%
            threshold = np.percentile(cdf, 40)
            # 找到截止点对应的原始像素值
            max_pix = np.argmax(cdf > threshold)
            # 创建掩码，高于截止点的像素
            mask = image_data > max_pix
            # 将高于截止点的像素设置为最大值
            image_data[mask] = np.iinfo(np.uint16).max

            threshold_min = np.percentile(cdf, 20)
            min_pix = np.argmax(cdf > threshold_min)
            # 创建掩码，高于截止点的像素
            mask_min = image_data < min_pix
            # 将高于截止点的像素设置为最大值
            image_data[mask_min] = np.iinfo(np.uint16).min

            # 线性映射
            max_val = 65535  # 16位图像的最大值
            scale = 255 / max_val
            offset = 255 - (max_pix * scale)

            # 应用映射
            stretched_image = cv2.convertScaleAbs(image_data, alpha=scale, beta=0)

            # 转换数据类型为8位无符号整数
            # stretched_image = stretched_image.astype(np.uint8)

            # 转换数据类型为8位无符号整数
            gray_image = stretched_image.astype(np.uint8)

            # cv2.imshow('Stretched Image', gray_image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            smoothed_image = cv2.GaussianBlur(gray_image, (9, 9), 2)
            # smoothed_image = smoothed_image.astype(np.uint8)
            # 边缘检测，例如使用Canny算法
            edges = cv2.Canny(smoothed_image, 50, 150)
            # 膨胀操作
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 1))  # 定义结构元素
            dilated_edges = cv2.dilate(edges, kernel, iterations=1)

            # 寻找膨胀后的轮廓
            contours, _ = cv2.findContours(dilated_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 初始化长宽比总和和轮廓数量
            aspect_ratio_sum = 0
            contour_count = 0

            # 遍历所有轮廓
            aspect_ratios = []
            line_count = 0
            big_area_count = 0
            line_in_contour_ratio = 0
            for contour in contours:
                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(contour)
                # print(f'--  {x}  {y}  {w}  {h}')
                # 计算长宽比，跳过高度为0的情况以避免除以零的错误

                if 100 < w*h < 8000:
                    if h != 0 and w != 0:
                        big_v = w if w > h else h
                        small_v = w if w < h else h
                        aspect_ratio = float(big_v) / small_v
                        aspect_ratio_sum += aspect_ratio
                        contour_count += 1
                        if aspect_ratio > 2:
                            line_count = line_count+1
                        aspect_ratios.append(aspect_ratio)
            if aspect_ratios:
                median_aspect_ratio = np.median(aspect_ratios)
                print(f"宽高比的中位数: {median_aspect_ratio:.2f}")
                line_in_contour_ratio = line_count/contour_count
                print(f'--  len:{len(contours)}  mean:{aspect_ratio_sum/contour_count}  {line_count}   {line_in_contour_ratio}')
            else:
                print("没有有效的宽高比数据。")

            # # 计算平均长宽比
            # if contour_count > 0:
            #     average_aspect_ratio = aspect_ratio_sum / contour_count
            #     print(f"所有轮廓的长宽比平均值: {average_aspect_ratio:.2f}")
            #
            #     # 判断平均长宽比是否大于3
            #     if average_aspect_ratio > 5:
            #         print("平均长宽比大于3，图像中可能存在条带形状分布")
            #     else:
            #         print("平均长宽比不大于3，图像中可能不存在条带形状分布")
            # else:
            #     print("没有找到有效的轮廓")

            image_rgb = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)

            # 创建图像的matplotlib图形
            fig, ax = plt.subplots(figsize=(gray_image.shape[1]/100, gray_image.shape[0]/100))
            ax.imshow(image_rgb, extent=[0, gray_image.shape[1], gray_image.shape[0], 0])

            # 遍历所有轮廓并绘制
            for contour in contours:
                # 提取轮廓的所有点的X和Y坐标
                points = contour.reshape(-1, 2)
                xs = points[:, 1]
                ys = points[:, 0]

                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(points)

                big_v = w if w > h else h
                small_v = w if w < h else h
                aspect_ratio = float(big_v) / small_v

                # 根据长宽比绘制不同颜色的轮廓
                if 100 < w*h < 8000:
                    if aspect_ratio > 2:
                        ax.plot(ys, xs, color='green')  # 长宽比大于2的轮廓用绿色绘制
                    else:
                        ax.plot(ys, xs, color='red')   # 其他轮廓用红色绘制

            # 显示图像
            # plt.show()

            if line_in_contour_ratio < 0.5:
                shutil.copy(fits_full_path, copy_ok_full_path)
                plt.savefig(png_ok_full_path, dpi=100, format='png', bbox_inches='tight')
                plt.close(fig)
            else:
                shutil.copy(fits_full_path, copy_err_full_path)
                plt.savefig(png_err_full_path, dpi=100, format='png', bbox_inches='tight')
                plt.close(fig)




