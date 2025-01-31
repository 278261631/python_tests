import os
from charset_normalizer import from_path

def detect_encoding(file_path):
    result = from_path(file_path).best()  # 检测编码
    return result.encoding


def batch_convert_txt_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                encoding = detect_encoding(file_path)
                print(f"Detected encoding:{file_path} {encoding}")

def batch_convert_txt_files_to_utf8(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='GB2312') as file:
                        content = file.read()

                    # 以UTF-8编码写入文件
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)

                    print(f"Converted {file_path} to UTF-8")
                except Exception as e:
                    print(f"Failed to convert {file_path}: {e}")


# 指定要转换的目录
dir_root = 'E:/tan_backup/PAT'
batch_convert_txt_files_to_utf8(dir_root)
