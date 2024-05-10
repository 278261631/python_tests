import os
from solve import config_manager
import sqlite3


# 连接到SQLite数据库
db_path = config_manager.ini_config.get('database', 'path')
temp_download_path = config_manager.ini_config.get('download', 'temp_download_path')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 1   limit 1000000
''')
result = cursor.fetchall()
file_error_count = 0
file_ok_count = 0
for idx, s_item in enumerate(result):
    file_name = "{}.fits".format(s_item[0])
    fis_file_path = os.path.join(temp_download_path, file_name)
    if (not os.path.exists(fis_file_path)) or os.path.getsize(fis_file_path) < 29000000:
        sql_str = f'UPDATE image_info SET status=0 WHERE id = {s_item[0]}'
        print(sql_str)
        cursor.execute(sql_str)
        file_error_count = file_error_count+1
    else:
        file_ok_count = file_ok_count+1
        print(os.path.getsize(fis_file_path))
    # print(os.path.getsize(fis_file_path))
    conn.commit()

    print(f'{idx} {file_error_count}/{file_ok_count} {len(result)}')


# 关闭游标和连接
cursor.close()
conn.close()

