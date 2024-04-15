import sqlite3

# 连接到SQLite数据库
# 如果数据库文件不存在，SQLite会自动创建它
conn = sqlite3.connect('fits_wcs.db')
cursor = conn.cursor()

# 创建一个表来存储所需的信息
# 假设我们有以下列：
# 'file_path' - 存储文件路径，使用TEXT类型
# 'wcs_info' - 存储WCS信息，使用TEXT类型
# 'fits_center_x' - 存储FITS图像的中心x坐标，使用FLOAT类型
# 'fits_center_y' - 存储FITS图像的中心y坐标，使用FLOAT类型
# 'fits_width' - 存储FITS图像的宽度，使用INTEGER类型
# 'fits_height' - 存储FITS图像的高度，使用INTEGER类型

cursor.execute('''
CREATE TABLE image_info (
    id          INTEGER        PRIMARY KEY AUTOINCREMENT,
    file_path   TEXT           NOT NULL,
    wcs_info    TEXT,
    center_v_x  DOUBLE         CHECK (center_v_x >= -1 AND center_v_x <= 1),
    center_v_y  DOUBLE         CHECK (center_v_y >= -1 AND center_v_y <= 1),
	center_v_z  DOUBLE         CHECK (center_v_y >= -1 AND center_v_y <= 1),
    a_v_x  DOUBLE         CHECK (a_v_x >= -1 AND a_v_x <= 1),
    a_v_y  DOUBLE         CHECK (a_v_y >= -1 AND a_v_y <= 1),
	a_v_z  DOUBLE         CHECK (a_v_z >= -1 AND a_v_z <= 1),
	center_a_theta  DOUBLE,
    b_v_x  DOUBLE         CHECK (b_v_x >= -1 AND b_v_x <= 1),
    b_v_y  DOUBLE         CHECK (b_v_y >= -1 AND b_v_y <= 1),
	b_v_z  DOUBLE         CHECK (b_v_z >= -1 AND b_v_z <= 1),
    center_b_theta  DOUBLE,
    status         DECIMAL

);

''')

# 提交更改
conn.commit()

# 关闭连接
conn.close()