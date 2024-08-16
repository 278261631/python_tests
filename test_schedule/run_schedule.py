import schedule
import time


def job():
    print("I'm working...")


schedule.every(5).seconds.do(job)

schedule.every().day.at("10:00:00").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)

