import os
import subprocess
from urllib.parse import urlparse

from solve.scan_by_days import scan_by_days
import sqlite3

import concurrent.futures
import subprocess
from threading import Lock

# 连接到SQLite数据库
conn = sqlite3.connect('../solve/fits_wcs.db')
cursor = conn.cursor()
temp_download_path = r'E:/test_download/thread/'
cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 111 order by id desc  limit 1000
''')
result = cursor.fetchall()
cursor.close()
conn.close()

lock = Lock()
progress_info = {}
# 最大同时下载的线程数
MAX_DOWNLOADS = 2


def wget_download(url, identifier):
    try:
        # 使用subprocess.Popen启动wget进程，并捕获输出
        file_name = "{}.fits".format(url[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        print(f'[{url[0]}]:       {identifier} / {len(result)}')
        with subprocess.Popen(["wget", "-O", save_file_path, "-nd", "--no-check-certificate", url[1]], stdout=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) \
                as proc:
            print("the commandline is {}".format(subprocess.args))
            for line in proc.stdout:
                # 从wget的输出中解析出下载进度
                if '%' in line:
                    progress = int(line.split('=')[1].split('%')[0].strip())
                    with lock:
                        progress_info[identifier] = progress
                        print(f"Download {identifier} progress: {progress}%")
    except Exception as ex:
        print(f"An error occurred: {ex}")
    finally:
        with lock:
            progress_info[identifier] = 100  # 标记下载完成
            print(f"Download {identifier} finished.")


with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_DOWNLOADS) as executor:
    # 使用字典推导式为每个URL创建一个下载任务
    # 每个任务都通过线程池中的线程执行wget_download函数
    futures = {executor.submit(wget_download, r_item, i): i for i, r_item in enumerate(result)}
    # 等待所有线程任务完成
    for future in concurrent.futures.as_completed(futures):
        identifier_i = futures[future]
        try:
            future.result()  # 获取线程返回的结果，确保异常被抛出
        except Exception as e:
            print(f"Thread for download {identifier_i} generated an exception: {e}")




