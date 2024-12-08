import argparse
import datetime
import os
import sqlite3


def run_03_2_check_from_txt(folder_name):

    # 连接到SQLite数据库
    db_path = '../thread_test/fits_wcs_recent.db'
    temp_txt_path = f'e:/fix_data/{folder_name}/'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if not os.path.exists(temp_txt_path):
        return
    files = os.listdir(temp_txt_path)
    for file_index, file in enumerate(files):
        if file.endswith('_chk.txt'):
            txt_full_path = os.path.join(temp_txt_path, file)
            with open(txt_full_path, 'r', encoding='utf-8') as txt_file:
                line = txt_file.readline()
                parts = line.split(',')
                # print(parts)
                # print(parts[20])
            len_parts = len(parts)
            if len_parts != 6:
                for i, item in enumerate(parts):
                    print(f'{i}:  {item}')
            assert len_parts == 6

            sql_str = f'UPDATE image_info SET  chk_exp_hist ="{parts[2]}", blob_dog_num={parts[3]},' \
                      f' chk_result={parts[4]}, status=1' \
                      f'  WHERE id = {parts[5]} and status=0 and chk_result is null'
            print(f'{sql_str}')
            if file_index % 100 == 0:
                conn.commit()
                print(f'{file_index} / {len(files)}')
            cursor.execute(sql_str)
            # if file_index > 100:
            #     break
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
    run_03_2_check_from_txt(folder_name)


if __name__ == "__main__":
    main()



