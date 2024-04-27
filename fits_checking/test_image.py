from math import sqrt

import matplotlib
import numpy as np
import sep
from astropy.io import fits
from matplotlib import pyplot as plt
from photutils.detection import DAOStarFinder
from skimage import filters
from skimage.filters import median

matplotlib.use('TkAgg')

# temp_download_path = r'E:/test_download/img_check/24751.fits'
# temp_download_path = r'E:/test_download/img_check/24900.fits'
temp_download_path = r'E:/test_download/img_check/24904.fits'
# temp_download_path = r'E:/test_download/img_check/15855.fits'
# temp_download_path = r'E:/test_download/img_check/8973.fits'
# temp_download_path = r'E:/test_download/img_check/18983.fits'
# temp_download_path = r'E:/test_download/img_check/18174.fits'
# temp_download_path = r'E:/test_download/img_check/20689.fits'
with fits.open(temp_download_path) as fits_hdul:
    hdul = fits_hdul
    image_data = hdul[0].data

    # todo check fits check focus
    from scipy.ndimage import gaussian_gradient_magnitude

    # sharpness = gaussian_gradient_magnitude(image_data, sigma=0.5)
    # median_value = np.median(sharpness)
    # print(f'sharp:   {median_value}')
    # plt.imshow(sharpness, cmap='gray')
    # plt.title('Sharpness Map')
    # plt.show()

    # 拖线 虚焦 重影?
    # todo check lines
    from skimage.feature import canny, blob_doh, blob_log, blob_dog, shape_index

    # mean = np.mean(image_data)
    # std = np.std(image_data)
    # # 设置西格玛系数，例如 n = 2
    # n = 15
    # # 计算 nσ 阈值
    # threshold = mean + n * std
    #
    # # 创建一个二值掩码，其中高于阈值的像素被设置为 1（或255），其余为 0
    # mask = image_data > threshold
    #
    # # 应用掩码到原始图像上
    # image_data = image_data * mask
    # image_data = filters.gaussian(image_data, sigma=100)
    # edges = canny(image_data, sigma=1)
    # print(f'canny edges:  {len(edges)}')
    # print(edges)
    # plt.imshow(edges, cmap='gray')
    # plt.title('Sharpness Map')
    # plt.show()

    # # # todo check source number
    # blobs_doh = blob_doh(image_data, max_sigma=30, threshold=0.01)
    # print(f'blobs:  {len(blobs_doh)}')

    # blobs_log = blob_log(image_data, max_sigma=30, num_sigma=10, threshold=0.1)
    # # Compute radii in the 3rd column.
    # blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)
    # print(f'{len(blobs_log)}')

    # blobs_dog = blob_dog(image_data, max_sigma=30, threshold=0.05)
    # blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)
    # print(f'{len(blobs_dog)}')

    # star_finder = DAOStarFinder(fwhm=1.0, threshold=100.0)
    # # 检测源
    # sources = star_finder(image_data)
    # print(f'  {len(sources)}')
    image_data_float = image_data.astype(np.float64)

    bkg = sep.Background(image_data_float)
    data_sub = image_data_float - bkg

    objects = sep.extract(data_sub, 10, err=bkg.globalrms)
    print(len(objects))

    # fig, ax = plt.subplots(figsize=(9, 3))
    # ax.imshow(edges, cmap='gray')
    # for blob in blobs_doh:
    #     y, x, r = blob
    #     c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
    #     ax.add_patch(c)
    # ax.set_axis_off()
    #
    # plt.tight_layout()
    # plt.show()
    #
    # target = 1
    # delta = 0.1
    # s = shape_index(image_data,sigma=1)
    # point_y, point_x = np.where(np.abs(s - target) < delta)
    #
    # print(f'shapes: {len(point_y)}')
    # print(f'shapes: {point_y}')
    #
    # fig, ax = plt.subplots(figsize=(9, 3))
    # ax.imshow(image_data, cmap='gray')
    # for idx, blob in enumerate(point_x):
    #     c = plt.Circle((point_x[idx], point_y[idx]), 4, color='red', linewidth=2, fill=False)
    #     ax.add_patch(c)
    # ax.set_axis_off()
    #
    # plt.tight_layout()
    # plt.show()
