import datetime
import re
import subprocess
import os


def scan_by_day_path(year_in_path, ymd_in_paht):
    # 最后的斜线很重要，否则wget np参数会不识别，造成下载其他不必要的数据
    download_url_root = f'https://download.china-vo.org/psp/east/{year_in_path}/{ymd_in_paht}/'
    # download_url_root = r'https://download.china-vo.org/psp/east/2023/20230511/P033_22.22%2B35.0/'
    temp_path = r'E:/test_download'
    print(f'path: {temp_path}')
    print(f'path: {download_url_root}')
    # 运行wget命令的spider功能，检查网站的链接，而不下载任何文件，并返回一个进程对象
    process = subprocess.Popen(["wget", "-N",
                                # ###   no download no dir creat
                                "--spider", "-nd",
                                "-r", "-np", "-nH", "-R", "index.html", "-P", temp_path, "--level=0",
                                # https 证书过期处理
                                "--no-check-certificate",
                                download_url_root], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("the commandline is {}".format(process.args))
    # 创建一个空的文件url列表
    file_url_list = []
    download_file_counter = 0
    # 迭代进程对象的输出，提取文件url
    for line in process.stderr:
        # 如果输出行以“--”开头，说明是一个文件url
        if line.startswith(b"--") and line.strip().endswith(b".fts"):
            # 去掉开头和结尾的空格和换行符，得到文件url
            file_url = line.strip()
            urls = re.findall(b'https?://\\S+', file_url)
            urls = [url.decode('utf-8') for url in urls]
            assert len(urls) == 1
            # 把文件url添加到文件url列表中
            file_url_list.extend(urls)

            print(urls)
            download_file_counter = download_file_counter + 1
        # print(line)

    # 将匹配到的URL从bytes转换为strings

    print(f'path>>: {len(file_url_list)}   /   {download_file_counter}')
    return file_url_list


def scan_by_days(yyyymmdd_str, day_count):
    # 创建开始日期
    year = int(yyyymmdd_str[:4])
    month = int(yyyymmdd_str[4:6])
    day = int(yyyymmdd_str[6:])
    start_date = datetime.datetime(year, month, day)
    file_url_list_all_days = []
    # 遍历日期区间
    for single_date in range(day_count):
        # 获取当前日期
        current_date = start_date + datetime.timedelta(days=single_date)
        # 执行操作，这里只是打印日期作为示例
        yyyy = current_date.strftime('%Y')
        yyyymmdd = current_date.strftime('%Y%m%d')
        print(current_date.strftime('%Y-%m-%d'))
        print(f'{yyyy}   {yyyymmdd}')
        url_list_by_day = scan_by_day_path(yyyy, yyyymmdd)
        file_url_list_all_days.extend(url_list_by_day)
    return file_url_list_all_days


scan_by_days('20231007', 2)
print("--------------")
