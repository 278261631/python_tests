import os
import shutil
import subprocess

from astropy.io import fits


def fits_file_check(fits_file_path):
    try:
        with fits.open(fits_file_path) as hdul:
            # 假设数据在第一个 HDU 中
            print(len(hdul[0].data))
            return True
    except Exception :
        print(f'False: {fits_file_path}')
        pass
    return False


def copy_or_download(fits_file_full_path, url, copy_file_full_path):

    if os.path.exists(fits_file_full_path):
        fits_file_check(fits_file_full_path)
    else:
        return False

    if os.path.exists(copy_file_full_path):
        shutil.copy(copy_file_full_path, fits_file_full_path)
    with subprocess.Popen(["wget", "-O", fits_file_full_path, "-nd", "--no-check-certificate", url],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) \
            as proc_down:
        print("the commandline is {}".format(proc_down.args))
        stdout_data, stderr_data = proc_down.communicate()
        if proc_down.returncode == 0:
            download_code = 1
        else:
            download_code = 301
            if stderr_data.decode().__contains__('ERROR 404'):
                download_code = 404
            os.remove(fits_file_full_path)
    print(f'{fits_file_full_path} code: {download_code}')
    if os.path.exists(fits_file_full_path):
        fits_file_check(fits_file_full_path)
    else:
        return False
