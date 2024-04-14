from solve.scan_by_days import scan_by_days
import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()

# 记录文件
url_list = scan_by_days('20231007', 1)

for idx, item in enumerate(url_list):
    # 首先检查file_path是否已存在
    cursor.execute('''
        SELECT 1 FROM image_info WHERE file_path = ?
    ''', (item,))
    result = cursor.fetchone()
    if not result:
        cursor.execute('''
            INSERT INTO image_info (file_path, status)
            VALUES (?,?)
        ''', (item, 0))
        if idx % 10 == 0:
            print(f'{idx}/ {len(url_list)} {item[idx]}')

# 提交所有更改
conn.commit()

# 下载文件
temp_download_path = r'E:/test_download/solve_temp'
print(f'path: {temp_download_path}')
cursor.execute('''
    SELECT id, file_path FROM image_info WHERE status = 0  limit 3
''')
result = cursor.fetchall()
for idx, s_item in enumerate(result):

    print(f'{idx} / {len(result)}')


# 解析fits wcs

# 加载wcs 更新数据库

# 关闭游标和连接
cursor.close()
conn.close()

