import os
from datetime import datetime

import matplotlib
import numpy as np
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from matplotlib import pyplot as plt
from photutils.detection import DAOStarFinder

matplotlib.use('TkAgg')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi']  # 常用中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常


# temp_download_pathA = r'D:\kats\temp_recent\20250616\gy1\K034-1.fits'
# temp_download_pathB = r'D:\kats\temp_recent\20250616\gy1\K034-1_no_trim.fits'
# input_dir = r'D:\kats\temp_recent\20250616\gy6'
input_dir = r'D:\kats\temp_recent\20250616\gy1'
time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
output_base_dir = f'png/{time_str}'

def extract_subimages(file_path, output_dir, tile_size=100, grid_size=(3, 3)):
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
    # y_step = height // grid_size[0]
    # x_step = width // grid_size[1]
    y_step_middle = height // (grid_size[0]+1)
    x_step_middle = width // (grid_size[1]+1)

    # 生成并保存子图
    fig, axes = plt.subplots(grid_size[0], grid_size[1], figsize=(10, 10))
    for i_grid in range(grid_size[0]):
        for j_grid in range(grid_size[1]):
            # 计算截取区域
            # y_start = i * y_step + (y_step - tile_size) // 2
            # x_start = j * x_step + (x_step - tile_size) // 2
            y_start = (i_grid + 1) * y_step_middle - (y_step_middle//2)
            x_start = (j_grid + 1) * x_step_middle - (x_step_middle//2)
            tile = data[y_start:y_start+tile_size, x_start:x_start+tile_size]

            # 可选：绘制子图预览
            ax = axes[i_grid, j_grid] if grid_size[0] > 1 else axes[j_grid]
            ax.imshow(tile, cmap='gray', origin='lower')
            ax.axis('off')

    base_name = os.path.splitext(os.path.basename(file_path))[0]  # 获取不带扩展名的文件名
    preview_filename = f'{base_name}_grid_preview.png'  # 构建新文件名
    # 保存网格预览图
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, preview_filename))
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

# extract_subimages(temp_download_pathA, 'png')
# extract_subimages(temp_download_pathB, 'png')


file_names = []
all_metrics = []
# 处理目录下所有FITS文件
for filename in os.listdir(input_dir):
    if filename.lower().endswith('.fits'):
        file_path = os.path.join(input_dir, filename)
        extract_subimages(file_path, output_base_dir)
        rms, fwhm, ellipticity, lm = check_image_quality(file_path)
        file_names.append(os.path.splitext(filename)[0])  # 存储文件名（不含扩展名）
        all_metrics.append([rms, fwhm, ellipticity, lm])

# 检查是否收集到文件数据
if not all_metrics:
    print("未找到任何FITS文件进行质量检查")
else:
    # 打印所有文件的质量指标
    print("\n图像质量指标对比:")
    for name, metrics in zip(file_names, all_metrics):
        rms, fwhm, ellipticity, lm = metrics
        print(f"{name} - RMS: {rms:.4f}, FWHM: {fwhm:.4f}, "
              f"Ellipticity: {ellipticity:.4f}, LM: {lm:.4f}")

    # 绘制质量对比图
    labels = ['RMS', 'FWHM', 'Ellipticity', 'LM']
    x = range(len(labels))

    plt.figure(figsize=(12, 6))

    # 设置条形宽度和间距
    bar_width = 0.8 / len(file_names)
    offset = np.arange(len(labels)) - (0.4 - bar_width / 2)

    # 为每个文件绘制条形
    for i, (name, metrics) in enumerate(zip(file_names, all_metrics)):
        plt.bar(offset + i * bar_width, metrics, width=bar_width, label=name)

    plt.xticks(x, labels)
    plt.xlabel('质量指标')
    plt.ylabel('数值')
    plt.title('多文件图像质量对比')
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    # plt.show()
    # 保存 plt
    plt.savefig(os.path.join(output_base_dir, f'quality_{time_str}.png'))