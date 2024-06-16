import os

import cv2
import matplotlib
import numpy as np
from astropy.io import fits
from astropy.table import Table
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from photutils.detection import DAOStarFinder
matplotlib.use('TkAgg')

if __name__ == '__main__':
    temp_txt_path = 'e:/fix_data/check'
    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        fits_id = os.path.basename(file).replace('.fits', '')
        if file.endswith('.fits'):
            fits_full_path = os.path.join(temp_txt_path, file)
            png_full_path = os.path.join(temp_txt_path, f'{fits_id}.png')
            print(f'{file_index}    {file}')
            with fits.open(fits_full_path) as hdul:
                image_data = hdul[0].data
            # 使用daofind检测最亮的100个星点
            star_finder = DAOStarFinder(fwhm=30.0, threshold=50.0, brightest=100)
            sources = star_finder(image_data)
            # print(sources)
            # sources.pprint(max_lines=-1, max_width=-1)
            roundness1_values = sources['roundness1']
            roundness2_values = sources['roundness2']
            mean_roundness1 = roundness1_values.mean()
            mean_roundness2 = roundness2_values.mean()
            print(f'round {file_index}  {fits_id} {mean_roundness1}   {mean_roundness2}')

            fig, ax = plt.subplots()
            ax.imshow(image_data, cmap='gray')  # 对于灰度图像使用 'gray' colormap

            # 添加红色圆圈标记
            # 假设我们知道要标记的圆心坐标和半径
            for s_item in sources:

                circle = Circle((s_item["xcentroid"], s_item["ycentroid"]), s_item["npix"]/100, edgecolor='red', facecolor='none')
                ax.add_patch(circle)

            # 保存图像到本地文件
            plt.savefig(png_full_path, dpi=300, format='png', bbox_inches='tight')
            plt.close(fig)
            # 关闭FITS文件
            # # 检查是否找到了100个星点
            # if len(sources) < 100:
            #     print(f"Only {len(sources)} sources were found, which is less than 100.")


        # break
