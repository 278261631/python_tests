import multiprocessing
import os
import sqlite3
import subprocess


# 连接到SQLite数据库
db_path = 'fits_wcs_2021.db'
temp_download_path = 'e:/2021/'

conn_search = sqlite3.connect(db_path)
cursor_search = conn_search.cursor()
remove_sql = f'SELECT id, file_path FROM image_info WHERE status = 100 and wcs_info is not null   limit 20000'
cursor_search.execute(remove_sql)
db_search_result = cursor_search.fetchall()
cursor_search.close()
conn_search.close()


if __name__ == '__main__':
    for rm_idx, search_item in enumerate(db_search_result):
        file_name = "{}.fits".format(search_item[0])
        save_file_path = os.path.join(temp_download_path, file_name)
        if os.path.exists(save_file_path):
            os.remove(save_file_path)
            print(f'XX  {rm_idx+1}/[{len(db_search_result)}]  {save_file_path}')
        else:
            print(f'--skip: {rm_idx+1}/[{len(db_search_result)}]  {save_file_path}')




