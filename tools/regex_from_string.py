import re

date_time_pattern = re.compile(r"UTC(\d{4})")
gy_pattern = re.compile(r"UTC(\d)")
k_pattern = re.compile(r"K(\d+)")


def get_yyyy_from_path(fits_url):
    year_month_day = '--'
    match = date_time_pattern.search(fits_url)
    if match:
        year_month_day = match.group(1)  # 年月日
    return year_month_day

