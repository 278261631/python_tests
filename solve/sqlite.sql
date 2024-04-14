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
    center_b_theta  DOUBLE

);

--
-- 由SQLiteStudio v3.3.3 产生的文件 周日 4月 14 17:06:33 2024
--
-- 文本编码：System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- 表：image_info
DROP TABLE IF EXISTS image_info;

CREATE TABLE image_info (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path      TEXT    NOT NULL,
    wcs_info       TEXT,
    center_v_x     DOUBLE  CHECK (center_v_x >= -1 AND
                                  center_v_x <= 1),
    center_v_y     DOUBLE  CHECK (center_v_y >= -1 AND
                                  center_v_y <= 1),
    center_v_z     DOUBLE  CHECK (center_v_y >= -1 AND
                                  center_v_y <= 1),
    a_v_x          DOUBLE  CHECK (a_v_x >= -1 AND
                                  a_v_x <= 1),
    a_v_y          DOUBLE  CHECK (a_v_y >= -1 AND
                                  a_v_y <= 1),
    a_v_z          DOUBLE  CHECK (a_v_z >= -1 AND
                                  a_v_z <= 1),
    center_a_theta DOUBLE,
    b_v_x          DOUBLE  CHECK (b_v_x >= -1 AND
                                  b_v_x <= 1),
    b_v_y          DOUBLE  CHECK (b_v_y >= -1 AND
                                  b_v_y <= 1),
    b_v_z          DOUBLE  CHECK (b_v_z >= -1 AND
                                  b_v_z <= 1),
    center_b_theta DOUBLE,
    status         DECIMAL
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;

