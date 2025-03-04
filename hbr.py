import time
import subprocess

def adb_run(args):
    subprocess.run([r"F:/platform-tools/adb.exe","-s","127.0.0.1:16384","shell"] + args)

def hbr_start():
    #打开进程
    print(f"HBR START")
    adb_run(["am","start","-n","com.bilibili.heaven/com.unity3d.player.UnityPlayerActivity"])
    time.sleep(2)
    adb_run(['monkey', '-p', "com.bilibili.heaven", '1'])
    for _ in range(300):
        time.sleep(1)
        adb_run(["input","tap",str(826),str(540)])
    for _ in range(300):
        time.sleep(1)
        adb_run(["input","tap",str(1190),str(52)])
    #关闭进程
    adb_run(["am","force-stop","com.bilibili.heaven"])
    print(f"HBR END")