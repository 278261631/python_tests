import os
import subprocess
from urllib.parse import urlparse

from solve.scan_by_days import scan_by_days
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()


# 下载文件
temp_download_path = r'E:/test_download/'
print(f'path: {temp_download_path}')
cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 0  limit 2
''')
result = cursor.fetchall()
for idx, s_item in enumerate(result):
    parsed_url = urlparse(s_item[1])
    # file_name = parsed_url.path.split('/')[-1].decode('utf-8')
    file_name = "{}.fits".format(s_item[0])
    save_file_path = os.path.join(temp_download_path, file_name)
    process = subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate",
                                s_item[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("the commandline is {}".format(process.args))
    process.communicate()
    print(f'{idx} / {len(result)}')
    # 检查wget的退出状态
    if process.returncode == 0:
        print("Download was successful.")
        cursor.execute('''
            UPDATE image_info
            SET status = ?
            WHERE id = ?
        ''', (1, s_item[0]))

    else:
        print("Download failed.")
        print("Error message:", process.stderr)
conn.commit()

# 解析fits wcs

# 加载wcs 更新数据库

# 关闭游标和连接
cursor.close()
conn.close()

