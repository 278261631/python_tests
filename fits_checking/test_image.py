from astropy.io import fits
from matplotlib import pyplot as plt

temp_download_path = r'E:/test_download/img_check/25025.fits'
with fits.open(temp_download_path) as fits_hdul:
    hdul = fits_hdul
    image_data = hdul[0].data

    # todo check fits check focus
    from scipy.ndimage import gaussian_gradient_magnitude

    sharpness = gaussian_gradient_magnitude(image_data, sigma=4)
    plt.imshow(sharpness, cmap='gray')
    plt.title('Sharpness Map')
    plt.show()

    # # todo check lines
    # from skimage.feature import canny
    # edges = canny(image_data)
    #
    # # todo check source number
    # from skimage.source_detector import detect_sources
    # sources = detect_sources(image_data, threshold=5.0, nlabels=2)
    #
