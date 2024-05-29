import datetime
import multiprocessing
import os
import sqlite3


if __name__ == '__main__':

    counter_success = 0
    counter_fail = 0
    # 连接到SQLite数据库
    db_path_157 = 'fits_wcs_2022_123.db'
    db_path_10 = 'fits_wcs_2022.db'
    conn_157 = sqlite3.connect(db_path_157)
    cursor_157 = conn_157.cursor()
    conn_10 = sqlite3.connect(db_path_10)
    cursor_10 = conn_10.cursor()

    sql_157 = f'SELECT * FROM image_info limit 70000'
    cursor_157.execute(sql_157)
    db_search_157 = cursor_157.fetchall()
    cursor_157.close()
    conn_157.close()

    for line_index, line in enumerate(db_search_157):
        v_2 = line[2]
        v_3 = line[3]
        v_4 = line[4]
        v_5 = line[5]
        v_6 = line[6]
        v_7 = line[7]
        v_8 = line[8]
        v_9 = line[9]
        v_10 = line[10]
        v_11 = line[11]
        v_12 = line[12]
        v_13 = line[13]
        v_14 = line[14]
        v_15 = line[15]
        v_16 = line[16]
        v_17 = line[17]
        v_18 = line[18]
        v_19 = line[19]
        v_20 = line[20]
        v_21 = line[21]
        v_22 = line[22]
        v_23 = line[23]
        if line[2] is None:
            v_2 = 'null'
        if line[3] is None:
            v_3 = 'null'
        if line[4] is None:
            v_4 = 'null'
        if line[5] is None:
            v_5 = 'null'
        if line[6] is None:
            v_6 = 'null'
        if line[7] is None:
            v_7 = 'null'
        if line[8] is None:
            v_8 = 'null'
        if line[9] is None:
            v_9 = 'null'
        if line[10] is None:
            v_10 = 'null'
        if line[11] is None:
            v_11 = 'null'
        if line[12] is None:
            v_12 = 'null'
        if line[13] is None:
            v_13 = 'null'
        if line[14] is None:
            v_14 = 'null'
        if line[15] is None:
            v_15 = 'null'
        if line[16] is None:
            v_16 = 'null'
        if line[17] is None:
            v_17 = 'null'
        if line[18] is None:
            v_18 = 'null'
        if line[19] is None:
            v_19 = 'null'
        if line[20] is None:
            v_20 = 'null'
        if line[21] is None:
            v_21 = 'null'
        if line[22] is None:
            v_22 = 'null'
        if line[23] is None:
            v_23 = 'null'

        sql_insert = f'INSERT INTO image_info (id, file_path, wcs_info, center_v_x, center_v_y, center_v_z, ' \
                     f'a_v_x, a_v_y, a_v_z, center_a_theta, b_v_x, b_v_y, b_v_z, center_b_theta, ' \
                     f'status, a_n_x, a_n_y, a_n_z, b_n_x, b_n_y, b_n_z, chk_exp_hist, chk_result, blob_dog_num) ' \
                     f'VALUES ({line[0]}, "{line[1]}", "{v_2}", {v_3}, {v_4}, {v_5},' \
                     f' {v_6}, {v_7}, {v_8}, {v_9}, {v_10}, {v_11}, {v_12}, {v_13},' \
                     f' {v_14}, {v_15}, {v_16}, {v_17}, {v_18}, {v_19}, {v_20}, {v_21}, {v_22}, {v_23})'

        print(sql_insert)
        if line_index % 100 == 0:
            conn_10.commit()
            print(f'process:  {line_index} /   {counter_success} / {counter_fail} / {len(db_search_157)}   ')
        try:
            cursor_10.execute(sql_insert)
            counter_success = counter_success+1
        except sqlite3.IntegrityError:
            print(f'--  {line[0] }')
            counter_fail = counter_fail+1
            continue

    conn_10.commit()
    cursor_10.close()
    conn_10.close()





