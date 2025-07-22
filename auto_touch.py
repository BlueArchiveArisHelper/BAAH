import schedule
import time
import datetime
import subprocess

from hbr import hbr_start
from fgo import fgo_start

def run_task(name):
    current_time = datetime.datetime.now()
    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["F:\\Python310\\python", ".\\main.py", name])
    if name.startswith("CN"):
        return subprocess.run(["F:\\Python310\\python", ".\\main.py", "CN_hard.json"])
    elif name.startswith("HK"):
        return subprocess.run(["F:\\Python310\\python", ".\\main.py", "HK_hard.json"])

# 定时任务
schedule.every().day.at("03:00").do(run_task, name = "HK_invite.json")
schedule.every().day.at("04:00").do(run_task, name = "CN_invite.json")
schedule.every().day.at("05:00").do(hbr_start)
schedule.every().day.at("05:30").do(fgo_start)
schedule.every().day.at("06:05").do(run_task, name = "HK_touch.json")
schedule.every().day.at("07:05").do(run_task, name = "CN_touch.json")
schedule.every().day.at("09:10").do(run_task, name = "HK_touch.json")
schedule.every().day.at("10:10").do(run_task, name = "CN_touch.json")
schedule.every().day.at("12:15").do(run_task, name = "HK_touch.json")
schedule.every().day.at("13:15").do(run_task, name = "CN_touch.json")
schedule.every().day.at("13:59:30").do(run_task, name = "CN_getFirst.json")

schedule.every().day.at("15:00").do(run_task, name = "HK_daily.json")
schedule.every().day.at("16:00").do(run_task, name = "CN_daily.json")
schedule.every().day.at("18:05").do(run_task, name = "HK_touch.json")
schedule.every().day.at("19:05").do(run_task, name = "CN_touch.json")
schedule.every().day.at("21:10").do(run_task, name = "HK_touch.json")
schedule.every().day.at("22:10").do(run_task, name = "CN_touch.json")
schedule.every().day.at("00:15").do(run_task, name = "HK_touch.json")
schedule.every().day.at("01:15").do(run_task, name = "CN_touch.json")

while True:
    schedule.run_pending()
    time.sleep(1)