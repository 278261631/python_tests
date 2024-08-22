import os
import sqlite3


def run_p_04_2_solve_from_txt():

    # 连接到SQLite数据库
    db_path = '../sources/fits_wcs_recent.db'
    temp_txt_path = 'e:/fix_data/2024/'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        if file.endswith('_solve.txt'):
            txt_full_path = os.path.join(temp_txt_path, file)
            with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
                line = txt_file.readline()
                parts = line.split(',')
                # print(parts)
                # print(parts[20])
            len_parts = len(parts)
            if len_parts != 24:
                for i, item in enumerate(parts):
                    print(f'{i}:  {item}')
            if parts[2] != '100':
                print(f'ss: {file_index}')
                continue
            assert len_parts == 24
            wcs_txt = f'{parts[3]},{parts[4]},{parts[5]}'
            # print(wcs_txt)

            sql_str = f'UPDATE image_info SET status={parts[2]}, wcs_info ="{wcs_txt}", center_v_x={parts[6]},' \
                      f' center_v_y={parts[7]}, center_v_z={parts[8]},' \
                      f' a_v_x={parts[9]}, a_v_y={parts[10]}, a_v_z={parts[11]},' \
                      f'center_a_theta={parts[12]},' \
                      f' b_v_x={parts[13]}, b_v_y={parts[14]}, b_v_z={parts[15]}, ' \
                      f'center_b_theta={parts[16]},' \
                      f'a_n_x={parts[17]}, a_n_y={parts[18]},a_n_z={parts[19]},' \
                      f'b_n_x={parts[20]}, b_n_y={parts[21]},b_n_z={parts[22]}' \
                      f'  WHERE id = {parts[23]} and status != 100'
            # print(sql_str)
            if file_index % 2 == 0:
                conn.commit()
                print(f'{file_index} / {len(files)}')
            cursor.execute(sql_str)
            # if file_index > 100:
            #     break
    conn.commit()
    cursor.close()
    conn.close()


def run_p_09_clean_dir():

    # 连接到SQLite数据库
    db_path = '../sources/fits_wcs_recent.db'
    temp_txt_path = 'e:/fix_data/2024/'
    conn_search = sqlite3.connect(db_path)
    cursor_search = conn_search.cursor()




    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        if file.endswith('_solve.txt'):
            txt_full_path = os.path.join(temp_txt_path, file)
            with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
                line = txt_file.readline()
                parts = line.split(',')
                # print(parts)
                # print(parts[20])
            len_parts = len(parts)
            if len_parts != 24:
                for i, item in enumerate(parts):
                    print(f'{i}:  {item}')
            if parts[2] != '100':
                print(f'ss: {file_index}')
                continue
            assert len_parts == 24

            sql_search = f'select id,file_path from  image_info where status = {parts[23]} and image_info.wcs_info is not null limit 1'
            print(sql_search)
            cursor_search.execute(sql_search)
            db_search_result = cursor_search.fetchall()
            if len(db_search_result) == 1:
                file_name_fits = os.path.join(temp_txt_path, f'{parts[23]}.fits')
                file_name_txt_ok = os.path.join(temp_txt_path, f'{parts[23]}_ok.txt')
                file_name_txt_chk = os.path.join(temp_txt_path, f'{parts[23]}_chk.txt')
                print(f'del : {file_name_fits}    {file_name_txt_ok}    {file_name_txt_chk}')
                # todo
    cursor_search.close()
    conn_search.close()





