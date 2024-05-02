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

create table image_info
(
    id             INTEGER
        primary key autoincrement,
    file_path      TEXT not null,
    wcs_info       TEXT,
    center_v_x     DOUBLE,
    center_v_y     DOUBLE,
    center_v_z     DOUBLE,
    a_v_x          DOUBLE,
    a_v_y          DOUBLE,
    a_v_z          DOUBLE,
    center_a_theta DOUBLE,
    b_v_x          DOUBLE,
    b_v_y          DOUBLE,
    b_v_z          DOUBLE,
    center_b_theta DOUBLE,
    status         DECIMAL,
    a_n_x          DOUBLE,
    a_n_y          DOUBLE,
    a_n_z          DOUBLE,
    b_n_x          DOUBLE,
    b_n_y          DOUBLE,
    b_n_z          DOUBLE,
    chk_exp_hist   INTEGER,
    chk_result     INTEGER,
    blob_dog_num   INTEGER,
    check (a_v_x >= - 1 AND a_v_x <= 1),
    check (a_v_y >= - 1 AND a_v_y <= 1),
    check (a_v_z >= - 1 AND a_v_z <= 1),
    check (b_v_x >= - 1 AND b_v_x <= 1),
    check (b_v_y >= - 1 AND b_v_y <= 1),
    check (b_v_z >= - 1 AND b_v_z <= 1),
    check (center_v_x >= - 1 AND center_v_x <= 1),
    check (center_v_y >= - 1 AND center_v_y <= 1),
    check (center_v_y >= - 1 AND center_v_y <= 1)
);



create table image_info
(
    id             INTEGER
        primary key autoincrement,
    file_path      TEXT not null,
    wcs_info       TEXT,
    center_v_x     DOUBLE,
    center_v_y     DOUBLE,
    center_v_z     DOUBLE,
    a_v_x          DOUBLE,
    a_v_y          DOUBLE,
    a_v_z          DOUBLE,
    center_a_theta DOUBLE,
    b_v_x          DOUBLE,
    b_v_y          DOUBLE,
    b_v_z          DOUBLE,
    center_b_theta DOUBLE,
    status         DECIMAL,
    a_n_x          DOUBLE,
    a_n_y          DOUBLE,
    a_n_z          DOUBLE,
    b_n_x          DOUBLE,
    b_n_y          DOUBLE,
    b_n_z          DOUBLE,
    check (a_v_x >= - 1 AND a_v_x <= 1),
    check (a_v_y >= - 1 AND a_v_y <= 1),
    check (a_v_z >= - 1 AND a_v_z <= 1),
    check (b_v_x >= - 1 AND b_v_x <= 1),
    check (b_v_y >= - 1 AND b_v_y <= 1),
    check (b_v_z >= - 1 AND b_v_z <= 1),
    check (center_v_x >= - 1 AND center_v_x <= 1),
    check (center_v_y >= - 1 AND center_v_y <= 1),
    check (center_v_y >= - 1 AND center_v_y <= 1)
);

create index ""
    on image_info (file_path);

create index file_path_index
    on image_info (file_path);


