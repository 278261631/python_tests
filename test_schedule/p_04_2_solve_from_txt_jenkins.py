import argparse
import datetime
import os
import sqlite3

from tools.send_message import send_amq, ProcessStatus


def run_p_04_2_solve_from_txt(folder_name):

    # 连接到SQLite数据库
    db_path = '../thread_test/fits_wcs_recent.db'
    temp_txt_path = f'e:/fix_data/{folder_name}/'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if not os.path.exists(temp_txt_path):
        return
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
                send_amq(f'{parts[1]}.fits', 42, ProcessStatus.FAILED)
                continue
            assert len_parts == 24
            wcs_txt = f'{parts[3]},{parts[4]},{parts[5]}'
            # print(wcs_txt)
            send_amq(f'{parts[23]}.fits', 42, ProcessStatus.DEFAULT)
            sql_str = f'UPDATE image_info SET status={parts[2]}, wcs_info ="{wcs_txt}", center_v_x={parts[6]},' \
                      f' center_v_y={parts[7]}, center_v_z={parts[8]},' \
                      f' a_v_x={parts[9]}, a_v_y={parts[10]}, a_v_z={parts[11]},' \
                      f'center_a_theta={parts[12]},' \
                      f' b_v_x={parts[13]}, b_v_y={parts[14]}, b_v_z={parts[15]}, ' \
                      f'center_b_theta={parts[16]},' \
                      f'a_n_x={parts[17]}, a_n_y={parts[18]},a_n_z={parts[19]},' \
                      f'b_n_x={parts[20]}, b_n_y={parts[21]},b_n_z={parts[22]}' \
                      f'  WHERE id = {parts[23]} and status != 100'
            print(sql_str)
            if file_index % 2 == 0:
                conn.commit()
                print(f'{file_index} / {len(files)}')
            cursor.execute(sql_str)
            # if file_index > 100:
            #     break
            send_amq(f'{parts[23]}.fits', 42, ProcessStatus.SUCCESS)
    conn.commit()
    cursor.close()
    conn.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Schedule job with optional time parameter.")
    parser.add_argument('--time', type=str, help='time in YYYYMMDD format')
    return parser.parse_args()


def main():
    current_time = datetime.datetime.now()
    args = parse_args()
    if args.time:
        try:
            current_time = datetime.datetime.strptime(args.time, '%Y%m%d')
        except ValueError:
            print("Invalid time format. Please use YYYYMMDD.")

    folder_name = current_time.strftime('%Y%m%d')
    run_p_04_2_solve_from_txt(folder_name)


if __name__ == "__main__":
    main()





