#!/usr/bin/env python3
"""
创建测试FITS文件用于演示监控系统
"""

import numpy as np
from astropy.io import fits
from astropy.time import Time
import os
from datetime import datetime

def create_test_fits_file(output_dir="test_fits_data"):
    """创建一个包含模拟星点的测试FITS文件"""
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建图像数据 (1024x1024像素)
    image_size = 1024
    image_data = np.random.normal(1000, 50, (image_size, image_size)).astype(np.float32)
    
    # 添加一些模拟的星点
    star_positions = [
        (200, 300), (400, 500), (600, 200), (800, 700),
        (150, 800), (900, 400), (300, 600), (700, 150)
    ]
    
    for x, y in star_positions:
        # 创建高斯星点
        star_flux = np.random.uniform(5000, 20000)
        fwhm = np.random.uniform(2.0, 4.0)
        sigma = fwhm / 2.355
        
        # 生成高斯分布
        y_indices, x_indices = np.ogrid[:image_size, :image_size]
        gaussian = star_flux * np.exp(-((x_indices - x)**2 + (y_indices - y)**2) / (2 * sigma**2))
        
        # 添加到图像中
        image_data += gaussian
    
    # 创建FITS header
    header = fits.Header()
    header['SIMPLE'] = True
    header['BITPIX'] = -32
    header['NAXIS'] = 2
    header['NAXIS1'] = image_size
    header['NAXIS2'] = image_size
    header['OBJECT'] = 'Test Field'
    header['TELESCOP'] = 'Test Telescope'
    header['INSTRUME'] = 'Test Camera'
    header['FILTER'] = 'V'
    header['EXPTIME'] = 60.0
    header['DATE-OBS'] = Time.now().isot
    header['RA'] = 180.0
    header['DEC'] = 45.0
    header['AIRMASS'] = 1.2
    header['GAIN'] = 1.5
    header['RDNOISE'] = 5.0
    header['PIXSCALE'] = 1.0
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_image_{timestamp}.fits"
    filepath = os.path.join(output_dir, filename)
    
    # 创建FITS文件
    hdu = fits.PrimaryHDU(image_data, header=header)
    hdu.writeto(filepath, overwrite=True)
    
    print(f"创建测试FITS文件: {filepath}")
    return filepath

if __name__ == "__main__":
    create_test_fits_file()
