import subprocess
import time
import schedule as schedule


def run_upload():
    process = subprocess.Popen(["curl", "-X",
                                "POST", "-F", "file=@E:/test.png", "http://localhost:8000/dashboard/upload",
                            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("the commandline is {}".format(process.args))
    for line in process.stderr:
        print(line)


# 每隔1分钟执行一次
# schedule.every(1).minute.do(run_upload)
# 每隔60秒执行一次
schedule.every(10).seconds.do(run_upload)
run_upload()
while True:
    schedule.run_pending()
    time.sleep(1)

