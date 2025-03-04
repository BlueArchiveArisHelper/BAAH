import time
import subprocess

def adb_run(args):
    subprocess.run([r"F:/platform-tools/adb.exe","-s","127.0.0.1:16384","shell"] + args)

def fgo_start():
    #打开进程
    print(f"FGO START")
    adb_run(["am","start","-n","com.mumu.launcher/com.mumu.launcher.Launcher"])
    # adb_run(["am","start","com.bilibili.fatego/com.bilibili.fatego.UnityPlayerNativeActivity"])
    time.sleep(2)
    adb_run(["input","tap",str(646),str(369)])
    time.sleep(10)
    adb_run(['monkey', '-p', "com.bilibili.fatego", '1'])
    for _ in range(30):
        time.sleep(10)
        adb_run(["input","tap",str(832),str(567)])
    #关闭进程
    adb_run(["am","force-stop","com.bilibili.fatego"])
    print(f"FGO END")