from astropy.io import fits
from skimage.util import img_as_float
from sklearn.svm import SVR


# 假设的BIQI特征提取函数
def extract_features(image):
    # 这里应该是提取图像特征的代码
    features = ...
    return features


# 假设的SVR模型训练函数
def trained_svr_model():
    svr = SVR(kernel='rbf', C=100, gamma=0.1)
    # 这里应该是使用训练数据训练SVR模型的代码
    return svr


# 从FITS文件加载图像
def load_image_from_fits(fits_file_path):
    with fits.open(fits_file_path) as hdul:
        # 假设图像数据存储在第一个HDU中
        image_data = hdul[0].data
        # 将图像数据转换为浮点型，以便进行特征提取
        image = img_as_float(image_data)
    return image


# BIQI测试demo
def biqi_demo(fits_image_path):
    # 从FITS文件加载图像
    image = load_image_from_fits(fits_image_path)

    # 提取特征
    features = extract_features(image)

    # 加载训练好的SVR模型
    svr_model = trained_svr_model()

    # 使用SVR模型预测图像质量分数
    score = svr_model.predict([features])

    return score


# 测试BIQI算法
fits_file_path = f'E:/fix_data/light_1.fits'
quality_score = biqi_demo(fits_file_path)
print(f"The predicted quality score of the image is: {quality_score}")