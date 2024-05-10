import os
from solve import config_manager
import sqlite3


# 连接到SQLite数据库
db_path = config_manager.ini_config.get('database', 'path')
temp_download_path = config_manager.ini_config.get('download', 'temp_download_path')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

file_names = []
# 遍历当前目录下的所有文件和文件夹
file_dirs = os.listdir(temp_download_path)
for idx, entry in enumerate(file_dirs):
    # 获取每个文件或文件夹的完整路径
    full_path = os.path.join(temp_download_path, entry)

    # 检查这个路径是文件还是文件夹
    if os.path.isfile(full_path):
        # print(f"文件: {full_path}")
        file_names.append(entry)
    elif os.path.isdir(full_path):
        print(f" pass  文件夹: {full_path}")
        pass
    if idx % 100 == 0:
        print(f'{idx} /{len(file_dirs)}   {len(file_names)}')

file_error_count = 0
file_ok_count = 0
for idx, s_item in enumerate(file_names):
    db_id = s_item.rstrip(".fits")
    fis_file_path = os.path.join(temp_download_path, s_item)
    if (not os.path.exists(fis_file_path)) or os.path.getsize(fis_file_path) < 29000000:
        sql_str = f'UPDATE image_info SET status=0 WHERE id = {db_id}'
        print(sql_str)
        cursor.execute(sql_str)
        file_error_count = file_error_count+1
    else:
        file_ok_count = file_ok_count+1
        # print(os.path.getsize(fis_file_path))
    # print(os.path.getsize(fis_file_path))
    conn.commit()
    if idx % 100 == 0:
        print(f'{idx} {file_error_count}/{file_ok_count} {len(file_names)}')

print(f'all:  {file_error_count}/{file_ok_count} {len(file_names)}')

# 关闭游标和连接
cursor.close()
conn.close()

