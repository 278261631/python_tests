from solve.scan_by_days import scan_by_days
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()

url_list = scan_by_days('20231007', 1)

for idx, item in enumerate(url_list):
    # 首先检查file_path是否已存在
    cursor.execute('''
        SELECT 1 FROM image_info WHERE file_path = ?
    ''', (item,))
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
            INSERT INTO image_info (file_path)
            VALUES (?)
        ''', (item,))
        if idx % 10 == 0:
            print(f'{idx}/ {len(url_list)} {item[idx]}')

# 提交所有更改
conn.commit()

# 关闭游标和连接
cursor.close()
conn.close()

