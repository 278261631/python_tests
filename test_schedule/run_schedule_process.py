import datetime

import schedule
import time

from test_schedule.p_02_download_or_copy import run_02_download
from test_schedule.p_03_1_download_check_to_txt import run_03_check_to_txt
from test_schedule.p_03_2_check_from_txt import run_03_2_check_from_txt
from test_schedule.p_04_1_solve_astap_to_txt import run_p_04_1_solve_astap_to_txt
from test_schedule.p_04_2_solve_from_txt import run_p_04_2_solve_from_txt, run_p_09_clean_dir
from test_schedule.t_01_scan import run_01_scan


def job_01():
    current_time = datetime.datetime.now()
    folder_name = current_time.strftime('%Y%m%d_%H%M%S')
    print(f'run at [{folder_name}]')
    run_01_scan()
    print(f'-----------  job_01  --------------')
    run_02_download(folder_name)
    print(f'-----------  job_02  --------------')
    run_03_check_to_txt(folder_name)
    print(f'-----------  job_03  --------------')
    run_03_2_check_from_txt(folder_name)
    print(f'-----------  job_04  --------------')
    run_p_04_1_solve_astap_to_txt(folder_name)
    print(f'-----------  job_05  --------------')
    run_p_04_2_solve_from_txt(folder_name)
    print(f'-----------  job_06  --------------')
    run_p_09_clean_dir(folder_name)
    print(f'-----------  job_09  --------------')


job_01()
schedule.every(60*60*4).seconds.do(job_01)


while True:
    schedule.run_pending()
    time.sleep(1)

