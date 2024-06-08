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
