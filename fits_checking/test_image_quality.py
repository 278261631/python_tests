import os

import matplotlib
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from matplotlib import pyplot as plt
from photutils.detection import DAOStarFinder

matplotlib.use('TkAgg')


temp_download_pathA = r'D:\kats\temp_recent\20250616\gy6\K034-1.fits'
temp_download_pathB = r'D:\kats\temp_recent\20250616\gy6\K034-1_no_trim.fits'


def extract_subimages(file_path, output_dir, tile_size=100, grid_size=(4, 4)):
    """
    从FITS文件中均匀截取网格化的小图并保存为PNG
    :param file_path: FITS文件路径
    :param output_dir: PNG输出目录
    :param tile_size: 单张小图尺寸 (默认100×100像素)
    :param grid_size: 网格划分维度 (默认3×3网格)
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 读取FITS数据
    with fits.open(file_path) as hdul:
        data = hdul[0].data

    # 获取图像尺寸
    height, width = data.shape

    # 计算网格步长
    y_step = height // grid_size[0]
    x_step = width // grid_size[1]

    # 生成并保存子图
    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(10, 10))
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # 计算截取区域
            y_start = i * y_step + (y_step - tile_size) // 2
            x_start = j * x_step + (x_step - tile_size) // 2
            tile = data[y_start:y_start+tile_size, x_start:x_start+tile_size]

            # 保存为PNG
            output_path = os.path.join(output_dir, f'tile_{i}_{j}.png')
            # plt.imsave(output_path, tile, cmap='gray', origin='lower')

            # 可选：绘制子图预览
            ax = axes[i, j] if grid_size[0] > 1 else axes[j]
            ax.imshow(tile, cmap='gray', origin='lower')
            ax.axis('off')

    base_name = os.path.splitext(os.path.basename(file_path))[0]  # 获取不带扩展名的文件名
    preview_filename = f'{base_name}_grid_preview.png'  # 构建新文件名
    # 保存网格预览图
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{preview_filename}_grid.png'))
    plt.close(fig)


# todo check rms fwhm ellipticity lm

# 定义函数来检查图像质量
def check_image_quality(file_path):
    hdul = fits.open(file_path)
    data = hdul[0].data
    hdul.close()

    # 计算背景统计量
    mean, median, std = sigma_clipped_stats(data, sigma=3.0)
    rms = std

    # 使用DAOStarFinder检测恒星
    daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
    sources = daofind(data - median)
    # 均匀的截取9张小图， 每张100*100 像素 ，保存为png


    # 这里简单假设第一个检测到的源代表图像质量
    # if len(sources) > 0:
    #     fwhm = sources['fwhm'][0]
    #     ellipticity = sources['ellipticity'][0]
    # else:
    #     fwhm = 0
    #     ellipticity = 0

    # 这里lm暂时用背景均值代替
    lm = mean

    return rms, 0, 0, lm

extract_subimages(temp_download_pathA, 'png')
extract_subimages(temp_download_pathB, 'png')

# 检查两个文件的图像质量
rms_A, fwhm_A, ellipticity_A, lm_A = check_image_quality(temp_download_pathA)
rms_B, fwhm_B, ellipticity_B, lm_B = check_image_quality(temp_download_pathB)

# 打印结果
print(f'File A - RMS: {rms_A}, FWHM: {fwhm_A}, Ellipticity: {ellipticity_A}, LM: {lm_A}')
print(f'File B - RMS: {rms_B}, FWHM: {fwhm_B}, Ellipticity: {ellipticity_B}, LM: {lm_B}')

# 绘制质量图
labels = ['RMS', 'FWHM', 'Ellipticity', 'LM']
values_A = [rms_A, fwhm_A, ellipticity_A, lm_A]
values_B = [rms_B, fwhm_B, ellipticity_B, lm_B]

x = range(len(labels))
plt.bar([i - 0.2 for i in x], values_A, 0.4, label='File A')
plt.bar([i + 0.2 for i in x], values_B, 0.4, label='File B')

plt.xticks(x, labels)
plt.xlabel('Quality Metrics')
plt.ylabel('Values')
plt.title('Image Quality Comparison')
plt.legend()
plt.show()
