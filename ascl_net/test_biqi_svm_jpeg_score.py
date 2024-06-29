import numpy as np
import os
import subprocess

import pywt
from pywt import wavedec2
from scipy.special import gammaln, expit
from scipy.stats import gamma
from skimage import io, color
from sklearn import svm


def detcoef2(type, C, S, level):
    if type == 'all':
        return S
    elif type == 'h':
        return S[1]
    elif type == 'v':
        return S[0]
    elif type == 'd':
        return S[2]
    else:
        raise ValueError("Type must be 'all', 'h', 'v', or 'd'")


def biqi(im):
    # 确保图像是灰度的
    if len(im.shape) != 2:
        im = np.dot(im[...,:3], [0.2989, 0.5870, 0.1140])

    # 计算统计量
    num_scales = 3

    # gam = np.arange(0.2, 10.001, 0.001)
    # r_gam = gamma(1. / gam) * gamma(3. / gam) / (gamma(2. / gam) ** 2)

    gam = np.arange(0.2, 10.001, 0.001)
    # 计算 r_gam，这里使用 expit 函数来替代原来的 gamma 函数
    r_gam = expit(gammaln(1. / gam) - 2 * gammaln(2. / gam) + gammaln(3. / gam))

    # C, S = wavedec2(im, num_scales, 'db9')
    # C, S = wavedec2(im, wavelet='db9', mode='symmetric')
    coeffs = wavedec2(im, wavelet='db9', mode='symmetric')
    stats = []
    for p in range(num_scales):
        # coeffs = detcoef2('all', C, S, p)

        horz, vert, diag = coeffs[1], coeffs[0], coeffs[2]
        h_horz = np.array(horz).flatten()
        h_vert = np.array(vert).flatten()
        h_diag = np.array(diag).flatten()

        mu_horz = np.mean(h_horz)
        sigma_sq_horz = np.mean((h_horz - mu_horz) ** 2)
        E_horz = np.mean(np.abs(h_horz - mu_horz))
        rho_horz = sigma_sq_horz / E_horz ** 2
        gam_horz = gam[np.argmin(np.abs(rho_horz - r_gam))]

        mu_vert = np.mean(h_vert)
        sigma_sq_vert = np.mean((h_vert - mu_vert) ** 2)
        E_vert = np.mean(np.abs(h_vert - mu_vert))
        rho_vert = sigma_sq_vert / E_vert ** 2
        gam_vert = gam[np.argmin(np.abs(rho_vert - r_gam))]

        mu_diag = np.mean(h_diag)
        sigma_sq_diag = np.mean((h_diag - mu_diag) ** 2)
        E_diag = np.mean(np.abs(h_diag - mu_diag))
        rho_diag = sigma_sq_diag / E_diag ** 2
        gam_diag = gam[np.argmin(np.abs(rho_diag - r_gam))]

        stats.append([mu_horz, sigma_sq_horz, gam_horz,
                      mu_vert, sigma_sq_vert, gam_vert,
                      mu_diag, sigma_sq_diag, gam_diag])

    # 构建特征向量
    # rep_vec = np.array(stats).flatten() //TODO flatten??
    rep_vec = np.array(stats)
    rep_vec = rep_vec[1:]  # 删除均值
    # 假设 rep_vec 是 numpy 数组


    # 打开文件进行写入
    with open('test_ind.txt', 'w') as f:
        for j in range(rep_vec.shape[0]):
            # 写入样本索引
            f.write(f'{j} ')
            for k in range(rep_vec.shape[1]):
                # 写入特征索引和对应的特征值
                f.write(f'{k}:{rep_vec[j, k]} ')
            # 写入换行符，开始新一行
            f.write('\n')

    import subprocess

    # 定义要执行的命令
    # scale_command = ['svm-scale', '-r', 'range2', 'test_ind.txt', '>>', 'test_ind_scaled']
    scale_command = ['svm-scale', '-r', 'range2', 'test_ind.txt']
    predict_command = ['svm-predict', '-b', '1', 'test_ind_scaled', 'model_89', 'output_89']

    scale_command_str = ' '.join(scale_command)
    predict_command_str = ' '.join(predict_command)

    # 打印实际执行的命令
    print("Executing scale command:", scale_command_str)
    print("Executing predict command:", predict_command_str)
    # 使用subprocess.run来执行命令
    # subprocess.run(scale_command)
    # 打开文件用于写入输出
    with open('test_ind_scaled', 'w') as f:
        # 运行命令，把输出重定向到打开的文件中
        subprocess.run(scale_command, stdout=f)
    subprocess.run(predict_command)

    # 在Python中删除文件
    import os
    os.remove('test_ind.txt')
    os.remove('test_ind_scaled')


    # 打开文件进行写入
    with open('test_ind.txt', 'w') as f:
        # 遍历 rep_vec 的每一行
        for j, row in enumerate(rep_vec):
            # 将行索引以浮点数格式写入（虽然这里它只是整数）
            f.write(f'{j:.0f} ')
            # 遍历行中的每个元素
            for k, value in enumerate(row):
                # 将特征索引和对应的特征值格式化为 "索引:值" 并写入
                f.write(f'{k}:{value} ')
            # 写入换行符，开始新一行
            f.write('\n')


    # subprocess.run(['svm-scale', '-r', 'range2_jp2k', 'test_ind.txt', '>>', 'test_ind_scaled'])
    scale_command = ['svm-scale', '-r', 'range2_jp2k', 'test_ind.txt']
    # 打开文件用于写入输出
    with open('test_ind_scaled', 'w') as f:
        # 运行命令，把输出重定向到打开的文件中
        subprocess.run(scale_command, stdout=f)
    subprocess.run(['svm-predict', '-b', '1', 'test_ind_scaled', 'model_89_jp2k', 'output_blur'])
    with open('output_blur', 'r') as f:
        # jp2k_score = float(f.read())
        jp2k_score = float(f.readline())
    os.remove('output_blur')
    os.remove('test_ind_scaled')

    # JPEG quality
    # jpeg_score = jpeg_quality_score(im)

    # WN quality
    # subprocess.run(['svm-scale', '-r', 'range2_wn', 'test_ind.txt', '>>', 'test_ind_scaled'])
    scale_command = ['svm-scale', '-r', 'range2_wn', 'test_ind.txt']
    # 打开文件用于写入输出
    with open('test_ind_scaled', 'w') as f:
        # 运行命令，把输出重定向到打开的文件中
        subprocess.run(scale_command, stdout=f)
    subprocess.run(['svm-predict', '-b', '1', 'test_ind_scaled', 'model_89_wn', 'output_blur'])
    with open('output_blur', 'r') as f:
        # wn_score = float(f.read())
        wn_score = float(f.readline())
    os.remove('output_blur')
    # 这里不需要再次删除 test_ind_scaled，因为它已经在上一步删除了

    # Blur quality
    # subprocess.run(['svm-scale', '-r', 'range2_blur', 'test_ind.txt', '>>', 'test_ind_scaled'])
    scale_command = ['svm-scale', '-r', 'range2_blur', 'test_ind.txt']
    # 打开文件用于写入输出
    with open('test_ind_scaled', 'w') as f:
        # 运行命令，把输出重定向到打开的文件中
        subprocess.run(scale_command, stdout=f)
    subprocess.run(['svm-predict', '-b', '1', 'test_ind_scaled', 'model_89_blur', 'output_blur'])
    with open('output_blur', 'r') as f:
        # blur_score = float(f.read())
        blur_score = float(f.readline())
    os.remove('output_blur')
    os.remove('test_ind.txt')  # 这里删除原始文件

    # # FF quality
    # # subprocess.run(['svm-scale', '-r', 'range2_ff', 'test_ind.txt', '>>', 'test_ind_scaled'])
    # scale_command = ['svm-scale', '-r', 'range2_ff', 'test_ind.txt']
    # # 打开文件用于写入输出
    # with open('test_ind_scaled', 'w') as f:
    #     # 运行命令，把输出重定向到打开的文件中
    #     subprocess.run(scale_command, stdout=f)
    # subprocess.run(['svm-predict', '-b', '1', 'test_ind_scaled', 'model_89_ff', 'output_blur'])
    # with open('output_blur', 'r') as f:
    #     # ff_score = float(f.read())
    #     ff_score = float(f.readline())
    # os.remove('output_blur')


    with open('output_89', 'r') as fid:
        # 跳过文件的第一行（如果需要）
        next(fid)
        # 读取所有行，使用逗号分隔的浮点数格式
        lines = fid.readlines()
        # 将每一行分割成单独的列，并转换成浮点数
        output = [list(map(float, line.strip().split(' '))) for line in lines]

    # 提取概率值，对应于 MATLAB 中 probs = output(:,2:end)
    probs = [row[1:] for row in output]

    # 计算最终的质量评分
    # 假设 scores 是一个列表，存储了各个维度的分数
    scores = [jp2k_score, wn_score, blur_score, blur_score, blur_score]
    # scores = [jp2k_score, jpeg_score, wn_score, wn_score, blur_score, ff_score]

    scores_array = np.array(scores)  # todo o???

    # quality = sum(p * s for p, s in zip(probs, scores))
    quality = np.sum(probs * scores_array, axis=1)

    # 删除文件 output_89
    os.remove('output_89')

    # clc 相当于清除控制台输出，在 Python 中通常不需要
    print("\n" * 100)  # 如果需要，可以用这种方式来清屏


    return quality


temp_jpeg_path = 'e:/fix_data/'
scores_list = []
files = os.listdir(temp_jpeg_path)
for file_index, file in enumerate(files):
    if file.endswith('.jpg'):
        jpg_full_path = os.path.join(temp_jpeg_path, file)
        original_image = io.imread(jpg_full_path)

        # 如果图像是彩色的，则将其转换为灰度图像
        image = color.rgb2gray(original_image)

        # 2. 调用 biqi 函数来计算质量得分：
        # quality = biqi(image)
        quality_score = biqi(image)

        # 打印质量得分
        print(f"The quality score of the image is: {quality_score}")
        scores_list.append((file, quality_score[0]))

print(f'=======================')
sorted_scores = sorted(scores_list, key=lambda x: x[1], reverse=True)
for file, score in sorted_scores:
    print(f"JPEG质量评分：{score}  {file}")