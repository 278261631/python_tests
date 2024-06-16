import os

import cv2
import matplotlib
import numpy as np
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from photutils.detection import DAOStarFinder
from skimage.color import rgb2gray

matplotlib.use('TkAgg')
from skimage import io, filters, measure, color, morphology, exposure

sigma = 10
if __name__ == '__main__':
    temp_txt_path = 'e:/fix_data/check-sigma'
    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        fits_id = os.path.basename(file).replace('.fits', '')
        if file.endswith('.fits'):
            fits_full_path = os.path.join(temp_txt_path, file)
            png_full_path = os.path.join(temp_txt_path, f'{fits_id}.png')
            print(f'{file_index}    {file}')
            with fits.open(fits_full_path) as hdul:
                image_data = hdul[0].data
            if len(image_data.shape) == 3:
                gray_image = rgb2gray(image_data)
            else:
                gray_image = image_data

            gray_image = exposure.equalize_adapthist(gray_image)
            # 背景估计，这里使用高斯滤波作为示例
            background = filters.gaussian(gray_image, sigma=sigma)

            # 背景减除
            difference = gray_image - background

            # 阈值化，分离前景和背景
            threshold_value = filters.threshold_otsu(difference)
            print(f't={threshold_value}   {difference[0].mean()} {background[0].mean()}')
            binary_image = difference > threshold_value

            # 形态学开运算，去除小的噪点
            cleaned_image = morphology.remove_small_objects(binary_image, 3)

            # 连通组件分析
            label_image = measure.label(cleaned_image)
            properties = measure.regionprops(label_image)

            # 筛选出可能是运动点的连通组件
            # 例如，排除面积过小的组件
            # motion_points = [prop for prop in properties if prop.area > 40]
            motion_points = [prop for prop in properties
                             if prop.axis_minor_length > 0 and prop.axis_major_length/prop.axis_minor_length > 2
                             and prop.area > 60]
            # print(motion_points)
            print(f'--{file_index}   {fits_id}  {len(motion_points)}')

            # 可视化
            fig, ax = plt.subplots(1)
            ax.imshow(gray_image, cmap='gray')
            # for point in motion_points:
            #     # 绘制连通组件的轮廓
            #     ax.plot(point.coords[:, 1], point.coords[:, 0], marker='o', color='red', linestyle='none')
            # 绘制空心圈

            for point in motion_points:
                centroid = point.centroid
                radius = np.sqrt(point.axis_major_length * point.axis_minor_length) / 4  # 估算半径
                # 使用circle函数绘制空心圈
                patch = plt.Circle((centroid[1], centroid[0]), radius, edgecolor='red', facecolor='none')
                ax.add_patch(patch)

            # plt.show()
            plt.savefig(png_full_path, dpi=300, format='png', bbox_inches='tight')
            plt.close(fig)
            plt.imsave(os.path.join(temp_txt_path, f'{fits_id}_dif.png'), difference, cmap='gray')
            plt.imsave(os.path.join(temp_txt_path, f'{fits_id}_bin.png'), binary_image, cmap='gray')
            plt.imsave(os.path.join(temp_txt_path, f'{fits_id}_bgg.png'), background, cmap='gray')


        # break
