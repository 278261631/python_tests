import datetime
import subprocess
import time
import schedule as schedule


def run_download():
    now = datetime.datetime.now()
    # yyyymmdd = f'{now.year}{now.month}{now.day}/'
    # yyyy = f'{now.year}'
    yyyy = '2023'
    yyyymmdd = '20231007'
    # 最后的斜线很重要，否则wget np参数会不识别，造成下载其他不必要的数据
    download_url_root = f'https://download.china-vo.org/psp/east/{yyyy}/{yyyymmdd}/'

    temp_path = r'E:/test_download'
    print(f'path: {temp_path}')
    print(f'path: {download_url_root}')

    # 运行wget命令的spider功能，检查网站的链接，而不下载任何文件，并返回一个进程对象
    process = subprocess.Popen(["wget", "-N",
                                # ###   no download no dir creat
                                # "--spider", "-nd",
                                "-r", "-np", "-nH", "-R", "index.html", "-P", temp_path, "--level=0",
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
            # 把文件url添加到文件url列表中
            file_url_list.append(file_url)
            print(file_url)
            download_file_counter += download_file_counter
        print(line)

    print(f'path>>: {len(file_url_list)}   /   {download_file_counter}')


# 每隔1分钟执行一次
schedule.every(1).minute.do(run_download)
# 每隔60秒执行一次
# schedule.every(60*1).seconds.do(run_download)
run_download()
while True:
    schedule.run_pending()
    time.sleep(1)

