from astropy.io import fits
from matplotlib import pyplot as plt

temp_download_path = r'E:/test_download/img_check/145.fits'
with fits.open(temp_download_path) as fits_hdul:
    hdul = fits_hdul
    image_data = hdul[0].data

    # todo check fits check focus
    from scipy.ndimage import gaussian_gradient_magnitude

    sharpness = gaussian_gradient_magnitude(image_data, sigma=1)
    # plt.imshow(sharpness, cmap='gray')
    # plt.title('Sharpness Map')
    # plt.show()

    # 拖线 虚焦 重影?
    # todo check lines
    from skimage.feature import canny, blob_doh

    edges = canny(image_data)
    print(len(edges))
    # print(edges)
    # plt.imshow(edges, cmap='gray')
    # plt.title('Sharpness Map')
    # plt.show()

    # # todo check source number
    blobs_doh = blob_doh(image_data, max_sigma=30, threshold=0.01)
    # 可视化检测结果
    fig, ax = plt.subplots(figsize=(9, 3))
    # 显示图像
    ax.imshow(edges, cmap='gray')
    # 绘制斑点位置
    print(len(blobs_doh))
    for blob in blobs_doh:
        y, x, r = blob
        c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
        ax.add_patch(c)

    # 关闭坐标轴
    ax.set_axis_off()

    plt.tight_layout()
    plt.show()
