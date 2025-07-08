import os
import subprocess
import traceback
from modules.configs.MyConfig import config
from modules.utils.log_utils import logging, istr, CN, EN
from modules.utils.subprocess_helper import subprocess_run
import time
import numpy as np
import cv2
import platform


def getNewestSeialNumber(use_config=None):
    # 如果传入指定的配置文件，就使用指定的配置文件
    target_config = config
    if use_config:
        target_config = use_config

    if target_config.userconfigdict["ADB_DIRECT_USE_SERIAL_NUMBER"]:
        # 得到完整的序列号，emulator-5554
        return target_config.userconfigdict["ADB_SEIAL_NUMBER"]
    elif target_config.userconfigdict["TARGET_PORT"] and target_config.userconfigdict["TARGET_IP_PATH"]:
        # 从配置文件里得到模拟器IP和端口
        return "{}:{}".format(target_config.userconfigdict["TARGET_IP_PATH"],
                              target_config.userconfigdict["TARGET_PORT"])
    else:
        logging.error({"zh_CN": "TARGET_IP_PATH或TARGET_PORT未设置", "en_US": "TARGET_IP_PATH or TARGET_PORT not set"})
        logging.warn({"zh_CN": "使用默认值：127.0.0.1:5555", "en_US": "127.0.0.1:5555 is used as default value"})
        return "127.0.0.1:5555"


def get_config_adb_path(use_config=None):
    target_config = config
    # 如果传入指定的配置文件，就使用指定的配置文件
    if use_config:
        target_config = use_config
    return target_config.userconfigdict['ADB_PATH']


# 判断是否有TARGET_PORT这个配置项
def disconnect_this_device():
    """Disconnect this device."""
    subprocess_run([get_config_adb_path(), "disconnect", getNewestSeialNumber()])

def reconnect_offline():
    """Reconnect to the device that was disconnected, or remove the offline status of the device."""
    subprocess_run([get_config_adb_path(), "reconnect", "offline"])

def kill_adb_server():
    """Kill the adb server."""
    subprocess_run([get_config_adb_path(), "kill-server"])


def connect_to_device(use_config=None):
    """Connect to a device with the given device port."""
    if use_config:
        subprocess_run([get_config_adb_path(use_config), "connect", getNewestSeialNumber(use_config)])
    else:
        subprocess_run([get_config_adb_path(), "connect", getNewestSeialNumber()])


def click_on_screen(x, y):
    """Click on the given coordinates."""
    subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), "shell", "input", "tap", str(int(x)), str(int(y))])

def swipe_on_screen(x1, y1, x2, y2, ms):
    """Swipe from the given coordinates to the other given coordinates."""
    subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), "shell", "input", "swipe", str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(int(ms))])

def convert_img(path):
    with open(path, "rb") as f:
        bys = f.read()
        bys_ = bys.replace(b"\r\n", b"\n")  # 二进制流中的"\r\n" 替换为"\n"
    with open(path, "wb") as f:
        f.write(bys_)


def screen_shot_to_global(use_config=None, output_png=False):
    """
    Take a screenshot and save it to the GlobalState.
    
    Params
    ------
    use_config: 期望使用的config对象，为None则使用全局导入的config
    output_png: 使用pipe截图方法时是否保存png图片。截图方法为png时永远会输出png
    """
    target_config = config
    if use_config:
        target_config = use_config
    whether_pipe = target_config.userconfigdict["SCREENSHOT_METHOD"] == "pipe"
    if not whether_pipe:
        # 方法一，重定向输出到文件
        filename = target_config.userconfigdict['SCREENSHOT_NAME']
        with open("./{}".format(filename),"wb") as out:
            subprocess_run([get_config_adb_path(target_config), "-s", getNewestSeialNumber(target_config), "shell", "screencap", "-p"], stdout=out)
        #adb 命令有时直接截图保存到电脑出错的解决办法-加下面一段即可
        if (platform.system() != "Linux"):
            convert_img("./{}".format(filename))
    else:
        # 方法二，使用cv2提取PIPE管道中的数据
        # 使用subprocess的Popen调用adb shell命令，并将结果保存到PIPE管道中
        process = subprocess.run([get_config_adb_path(target_config), "-s", getNewestSeialNumber(target_config), "shell", "screencap", "-p"], stdout=subprocess.PIPE)
        # 读取管道中的数据
        screenshot = process.stdout
        # 将读取的字节流数据的回车换行替换成'\n'
        if platform.system() not in ["Linux", "Darwin"]:
            binary_screenshot = screenshot.replace(b'\r\n', b'\n')
        else:
            # Linux和Macos系统不需要替换
            binary_screenshot = screenshot
        # 使用numpy和imdecode将二进制数据转换成cv2的mat图片格式
        if (binary_screenshot == b''):
            logging.error({"zh_CN": "pipe截图失败", "en_US": "Failed to take pipe screenshot"})
            target_config.sessiondict["SCREENSHOT_DATA"] = None
            return
        img_screenshot = cv2.imdecode(np.frombuffer(binary_screenshot, np.uint8), cv2.IMREAD_COLOR)
        target_config.sessiondict["SCREENSHOT_DATA"] = img_screenshot
        if output_png:
            cv2.imwrite("./{}".format(target_config.userconfigdict['SCREENSHOT_NAME']), img_screenshot)


def get_now_running_app(use_config=None):
    """
    获取当前运行的app的前台activity
    """
    if use_config:
        output = subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), 'shell', 'dumpsys', 'window']).stdout
    else:
        output = subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'dumpsys', 'window']).stdout
    # adb shell "dumpsys window | grep mCurrentFocus"
    # 有时候启动器排前，应用排后，这里逆序排序
    for sentence in output.split("\n")[::-1]:
        if "mCurrentFocus" in sentence:
            # 找到当前运行的app activity
            # 判断是否有null，是null就继续查看后面的mCurrentFocus行
            if "null" in sentence:
                logging.warn({"zh_CN": ">>> MUMU模拟器需要设置里关闭保活！ <<<",
                              "en_US": "If you are using MUMU emulator, please turn off the keep alive in the settings!"})
                continue
            else:
                # 找到第一行不是null的app activity
                # 截取app activity
                try:
                    app_activity = sentence.split(" ")[-1].split("}")[0]
                    return app_activity
                except Exception as e:
                    logging.warn({"zh_CN": "截取当前运行的app名失败：{}".format(output),
                                "en_US": "Failed to get the current running app name:{}".format(output)})
                    break
    return output


def get_now_running_app_entrance_activity(use_config=None):
    """
    得到当前app的入口activity

    https://stackoverflow.com/questions/12698814/get-launchable-activity-name-of-package-from-adb/41325792#41325792
    """
    # 先获取当前运行的app的前台activity
    front_activity = get_now_running_app(use_config)
    logging.info({"zh_CN": "当前运行的app的前台activity是：{}".format(front_activity),
                  "en_US": "The foreground activity of the currently running app is: {}" .format (front_activity)})
    # 提取出包名
    package_name = front_activity.split("/")[0]
    if use_config:
        output = subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), 'shell', 'cmd', 'package', 'resolve-activity', '--brief', package_name]).stdout
    else:
        output = subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(),  'shell', 'cmd', 'package', 'resolve-activity', '--brief', package_name]).stdout
    # 提取出入口activity
    strlist = output.split()
    entrance_activity = strlist[-1]
    if "/" not in entrance_activity:
        logging.error({"zh_CN": f"获取入口activity失败：{output}",
                       "en_US":f"Failing to get entrance activity: {output}"})
        return entrance_activity
    return entrance_activity


def check_app_running(activity_path: str) -> bool:
    """
    检查app是否在运行，不校验app的activity,只校验app的名字
    """
    try:
        app_name = activity_path.split("/")[0]
    except Exception as e:
        logging.error({"zh_CN": "activity_path格式错误", "en_US": "The format of activity_path is wrong"})
        return False
    # 获取当前运行的app
    output = get_now_running_app()
    logging.info({"zh_CN": "运行中...当前运行的app是：{}".format(output),
                  "en_US": "Running...The currently running app is: {}".format(output)})
    if app_name in output:
        return True
    else:
        return False


def open_app(activity_path: str):
    """
    使用adb打开app
    """
    brand_waydroid = False
    try:
        # https://github.com/MaaXYZ/MaaFramework/issues/548
        # check waydroid, open in full screen
        check_brand = subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'getprop', 'ro.product.brand']).stdout
        if "waydroid" in check_brand.lower():
            brand_waydroid = True
            logging.info("waydroid detected")
    except Exception as e:
        logging.error(f"Error when check brand: {e}")
        pass
    # ==============================
    if brand_waydroid:
        subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'am', 'start', '--windowingMode', '4', activity_path], isasync=True)
    else:
        subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'am', 'start', activity_path], isasync=True)
    time.sleep(1)
    # 加-n参数，可以在已经启动的时候，切换activity而不只是包
    subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'am', 'start', '-n', activity_path], isasync=True)
    time.sleep(1)
    appname = activity_path.split("/")[0]
    subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'monkey', '-p', appname, '1'], isasync=True)

def close_app(activity_path: str):
    """
    使用adb关闭app
    """
    appname = activity_path.split("/")[0]
    subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), 'shell', 'am', 'force-stop', appname], isasync=True)

def get_wm_size(use_config=None):
    """
    获取屏幕分辨率结果，例如 Physical size: 720x1280
    """
    if not use_config:
        use_config = config
    # only focus on last line
    wmres = subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "size"]).stdout.strip().split("\n")[-1]
    return wmres

def get_dpi(use_config=None):
    """
    获取屏幕dpi结果，例如 Physical density: 320
    """
    if not use_config:
        use_config = config
    # only focus on last line (Physical density, Override density)
    dpires = subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "density"]).stdout.strip().split("\n")[-1]
    return dpires

def set_dpi(target_dpi, use_config=None):
    """
    set DPI
    """
    if not use_config:
        use_config = config
    if isinstance(target_dpi, float):
        target_dpi = int(target_dpi)
    subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "density", str(target_dpi)], isasync=True)

def set_wm_size(size=[], use_config=None):
    """
    设置屏幕分辨率
    """
    if not use_config:
        use_config = config
    if len(size) == 0:
        raise Exception("size is empty")
    subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "size", f"{size[0]}x{size[1]}"], isasync=True)
    
def reset_dpi(use_config=None):
    """
    重置屏幕dpi
    """
    if not use_config:
        use_config = config
    subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "density", "reset"], isasync=True)
    
def reset_wm_size(use_config=None):
    """
    重置屏幕分辨率
    """
    if not use_config:
        use_config = config
    subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "wm", "size", "reset"], isasync=True)

def check_shizuku(use_config=None):
    """
    检查shizuku是否安装
    """
    package_list = subprocess_run([get_config_adb_path(use_config), "-s", getNewestSeialNumber(use_config), "shell", "pm", "list", "packages"]).stdout()
    if "moe.shizuku.privileged.api" in package_list:
        return True
    else:
        return False

def install_apk(filepath):
    status = subprocess_run([get_config_adb_path(), "-s", getNewestSeialNumber(), "install", filepath], isasync=True)
    if status.returncode != 0:
        raise(Exception(istr({"zh_CN": "安装失败", "en_US": "Installation failed"})))
    
def install_dir(dir):
    command = f"{get_config_adb_path()} -s {getNewestSeialNumber()} install-multiple"
    for filename in os.listdir(dir):
        if filename.endswith(".apk"):
            command = command + f" {dir}/{filename}"
    status = os.system(command)
    if status != 0:
        raise(Exception(istr({"zh_CN": "安装失败", "en_US": "Installation failed"})))

# NO_NEED = "NO_NEED"
# ERROR = "ERROR"
# FAILED = "FAILED"
# SUCCESS = "SUCCESS"
# NO_FILE = "NO_FILE"
# def mumu_rm_mu(use_config=None) -> str:
#     """删除mumu的mu_bak文件，需要mumu开启root且读写系统文件权限"""

    
#     if use_config:
#         this_config = use_config
#     else:
#         this_config = config
#     try:
#         # 获取屏幕分辨率
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "wm", "size"]).stdout
#         height = int(output.split(":")[1].split("x")[0])
#         width = int(output.split(":")[1].split("x")[1])
#         print(width, height)
#         # 检查mumu是否有mu_bak文件
#         # adb -s 127.0.0.1:16416 shell "cd /system/xbin && ls"
#         logging.info({"zh_CN": "检查mu_bak文件", "en_US": "Checking mu_bak file"})
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "cd /system/xbin && ls"]).stdout
#         logging.info(output.split())
#         if ("mu_bak" in output.split()):
#             logging.info({"zh_CN": "模拟器检测到mu_bak文件", "en_US": "mu_bak file detected in the emulator"})
#         else:
#             return NO_NEED
#         # 将mu_bak文件保存到DATA文件夹下，如果已经在文件夹里了就跳过
#         if not os.path.exists("DATA/mu_bak"):
#             logging.info({"zh_CN": "保存mu_bak文件至本地", "en_US": "Saving mu_bak file to local"})
#             # adb -s
#             subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "pull", "/system/xbin/mu_bak", "DATA/mu_bak"])
#         # 解锁
#         # adb -s 127.0.0.1:16416 shell pm unsuspend com.nemu.superuser
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "pm", "unsuspend", "com.nemu.superuser"]).stdout
#         logging.info(output)
#         # 删除mu_bak文件
#         logging.info({"zh_CN": "删除模拟器mu_bak文件", "en_US": "Deleting mu_bak file in the emulator"})
#         # adb -s 127.0.0.1:16416 shell "su & rm -rf /system/xbin/mu_bak"
#         subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "su", "-c", "\"rm -rf /system/xbin/mu_bak\""], isasync=True)
#         time.sleep(1)
#         # adb点击 (761, 629)
#         subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "input", "tap", str(int(width*761/1280)), str(int(height*629/720))])
#         time.sleep(2)
#         # 检测是否删除成功
#         logging.info({"zh_CN": "检查mu_bak文件", "en_US": "Checking mu_bak file"})
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "cd /system/xbin && ls"]).stdout
#         logging.info(output.split())
#         if ("mu_bak" in output.split()):
#             logging.info({"zh_CN": "检查ROOT权限开启，以及磁盘共享可写系统盘", "en_US": "check if ROOT permission is enabled and disk sharing is writable"})
#             return FAILED
#         return SUCCESS
#     except Exception as e:
#         logging.error({"zh_CN": "删除mu_bak文件失败：{}".format(e), "en_US": "Failed to delete mu_bak file:{}".format(e)})
#         traceback.print_exc()
#         return ERROR
    
# def mumu_bak_mu(use_config=None) -> str:
#     """将mu_bak文件还原，需要mumu开启root且读写系统文件权限"""
    
#     if use_config:
#         this_config = use_config
#     else:
#         this_config = config
#     try:
#         # 检查mumu是否有mu_bak文件
#         # adb -s 127.0.0.1:16416 shell "cd /system/xbin && ls"
#         logging.info({"zh_CN": "检查mu_bak文件", "en_US": "Checking mu_bak file"})
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "cd /system/xbin && ls"]).stdout
#         logging.info(output.split())
#         if ("mu_bak" not in output.split()):
#             logging.info({"zh_CN": "模拟器没有检测到mu_bak文件", "en_US": "no mu_bak file detected in the emulator"})
#         else:
#             return NO_NEED
#         # 解锁
#         # adb -s 127.0.0.1:16416 shell pm unsuspend com.nemu.superuser
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "pm", "unsuspend", "com.nemu.superuser"]).stdout
#         logging.info(output)
#         # 粘贴mu_bak文件
#         if not os.path.exists("DATA/mu_bak"):
#             logging.info({"zh_CN": "DATA/mu_bak文件不存在", "en_US": "DATA/mu_bak file not found"})
#             return NO_FILE
#         logging.info({"zh_CN": "粘贴mu_bak文件", "en_US": "Add mu_bak file"})
#         # adb push DATA/mu_bak /data/local/tmp/mu_bak
#         # adb shell su -c "cp /data/local/tmp/mu_bak /system/xbin/mu_bak"
#         subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "push", "DATA/mu_bak", "/data/local/tmp/mu_bak"])
#         subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "su", "-c", "\"cp /data/local/tmp/mu_bak /system/xbin/mu_bak\""], isasync=True)
#         time.sleep(1)
#         # adb点击 (761, 629)
#         subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "input", "tap", str(761), str(629)])
#         time.sleep(2)
#         # 检测是否粘贴成功
#         logging.info({"zh_CN": "检查mu_bak文件", "en_US": "Checking mu_bak file"})
#         output = subprocess_run([get_config_adb_path(this_config), "-s", getNewestSeialNumber(this_config), "shell", "cd /system/xbin && ls"]).stdout
#         logging.info(output.split())
#         if ("mu_bak" not in output.split()):
#             logging.info({"zh_CN": "检查ROOT权限开启，以及磁盘共享可写系统盘", "en_US": "check if ROOT permission is enabled and disk sharing is writable"})
#             return FAILED
#         return SUCCESS
#     except Exception as e:
#         logging.error({"zh_CN": "mu_bak文件还原失败：{}".format(e), "en_US": "Failed to restore mu_bak file:{}".format(e)})
#         traceback.print_exc()
#         return ERROR

# ========================================
# minitouch：https://github.com/openstf/minitouch
# adb shell getprop ro.product.cpu.abi
# adb push minitouch /data/local/tmp
# adb shell chmod 755 /data/local/tmp/minitouch
# adb forward tcp:1111 localabstract:minitouch
# adb shell /data/local/tmp/minitouch
# 创建socket连接到localhost:1111，然后发送"m 0 20 40 50\n"，即可模拟点击事件

# maatouch：https://github.com/MaaAssistantArknights/MaaTouch
# adb push touch.zip /data/local/tmp/touch.jar
# adb shell chmod 755 /data/local/tmp/touch.jar
# adb shell export CLASSPATH=/data/local/tmp/touch.jar; app_process /data/local/tmp com.shxyke.touchevent.App
# 启动后直接交互
# ========================================

class MaaTouchUtils:
    """
    使用maatouch的工具类，初始化后需要call load_config()方法
    """
    def __init__(self):
        self.config = None
        self.adb_path = None
        self.adb_serial = None
        self.maatouch_process = None
        self.fail_init = False
        self.time_step = 20 # 细粒度20ms

    def load_config(self, config):
        self.config = config
        self.adb_path = get_config_adb_path(config)
        self.adb_serial = getNewestSeialNumber(config)
        
    def _initialize(self):
        """初始化maatouch，如果已经初始化过了就不再初始化，返回MaaTouch控制进程是否可用"""
        if self.maatouch_process and self.maatouch_process.poll() is None:
            # 运行中
            return True
        if self.fail_init:
            # 初始化失败过，不再初始化
            return False
        # 检查在/data/local/tmp是否有touch.jar
        jar_name = "_touch.jar"
        completed_process = subprocess_run([self.adb_path, "-s", self.adb_serial, "shell", "ls", "/data/local/tmp"])
        if jar_name not in completed_process.stdout:
            # 没有的话，需要推送
            logging.info({"zh_CN": "没有touch.jar，需要推送", "en_US": "No touch.jar found, need to push."})
            # 检查本地是否有touch.zip
            if not os.path.exists("./DATA/touch.zip"):
                logging.error({"zh_CN": "本地没有touch.zip", "en_US": "No touch.zip found locally"})
                self.fail_init = True
                return False
            # 推送touch.zip
            completed_process = subprocess_run([self.adb_path, "-s", self.adb_serial, "push", "./DATA/touch.zip", f"/data/local/tmp/{jar_name}"])
            logging.info(completed_process.stdout)
        # 给予执行权限
        completed_process = subprocess_run([self.adb_path, "-s", self.adb_serial, "shell", "chmod", "755", f"/data/local/tmp/{jar_name}"])
        # 启动maatouch
        self.maatouch_process = subprocess_run([self.adb_path, "-s", self.adb_serial, "shell", f'export CLASSPATH=/data/local/tmp/{jar_name}; app_process /data/local/tmp com.shxyke.touchevent.App'], isasync=True)
        logging.info(f"maatouch pid: {self.maatouch_process.pid}")
        time.sleep(0.5)
        # 检查是否启动成功
        if self.maatouch_process.poll() is None: # poll()返回None表示进程正在运行
            logging.info({"zh_CN": "maatouch启动成功", "en_US": "maatouch started successfully"})
            return True
        else:
            logging.error({"zh_CN": "maatouch启动失败", "en_US": "Failed to start maatouch"})
            self.fail_init = True
            return False
        
    def _check_init(func):
        """封装装饰器，检查是否初始化成功"""
        def wrapper(self, *args, **kwargs):
            if not self._initialize():
                logging.error(istr({CN: "maatouch初始化失败", EN: "Failed to initialize maatouch"}))
                return None
            else:
                res = func(self, *args, **kwargs)
                return res
        return wrapper
    
    # ===============析构函数===================
    def __del__(self):
        if self.maatouch_process and self.maatouch_process.poll() is None:
            self.maatouch_process.terminate()
            logging.info(istr({CN: "maatouch进程已终止", EN: "maatouch process has been terminated"}))
    
    # ===============操作函数===================

    @_check_init
    def _press_down(self, id:int, x, y, pressure):
        assert isinstance(id, int)
        x = int(x)
        y = int(y)
        pressure = int(pressure)
        finger_str = f"d {id} {x} {y} {pressure}\nc\n"
        self.maatouch_process.stdin.write(finger_str)
        self.maatouch_process.stdin.flush()
    
    @_check_init
    def _press_up(self, id:int):
        assert isinstance(id, int)
        finger_str = f"u {id}\nc\n"
        self.maatouch_process.stdin.write(finger_str)
        self.maatouch_process.stdin.flush()

    @_check_init
    def _press_move(self, id:int, x, y, pressure):
        assert isinstance(id, int)
        x = int(x)
        y = int(y)
        pressure = int(pressure)
        finger_str = f"m {id} {x} {y} {pressure}\nc\n"
        self.maatouch_process.stdin.write(finger_str)
        self.maatouch_process.stdin.flush()

    @_check_init
    def _press_reset(self):
        self.maatouch_process.stdin.write("r\nc\n")
        self.maatouch_process.stdin.flush()

    @_check_init
    def _key_onceclick(self, key:int):
        assert isinstance(key, int)
        key_str = f"k {key} o\nc\n"
        self.maatouch_process.stdin.write(key_str)
        self.maatouch_process.stdin.flush()

    @_check_init
    def _key_down(self, key:int):
        assert isinstance(key, int)
        key_str = f"k {key} d\nc\n"
        self.maatouch_process.stdin.write(key_str)
        self.maatouch_process.stdin.flush()
    
    @_check_init
    def _key_up(self, key:int):
        assert isinstance(key, int)
        key_str = f"k {key} u\nc\n"
        self.maatouch_process.stdin.write(key_str)
        self.maatouch_process.stdin.flush()

    # ============功能函数==================

    def sleep_ms(self, ms):
        """休眠ms毫秒"""
        time.sleep(ms / 1000)

    def click(self, x, y):
        self._press_down(0, x, y, 100)
        self._press_up(0)

    def swipe(self, x1, y1, x2, y2, ms):
        x_step = (x2 - x1) / ms
        y_step = (y2 - y1) / ms
        self._press_down(0, x1, y1, 100)
        # 细粒度20ms
        for i in range(self.time_step, ms, self.time_step):
            self.sleep_ms(self.time_step)
            self._press_move(0, x1 + x_step * i, y1 + y_step * i, 100)
        # 最后一步
        self.sleep_ms(ms % self.time_step)
        self._press_move(0, x2, y2, 100)
        self._press_up(0)

    def zoom(self, center_x, center_y, radius_from, radius_to, ms):
        # 从中心点左右开始按下
        self._press_down(0, center_x - radius_from, center_y, 100)
        self._press_down(1, center_x + radius_from, center_y, 100)
        x_step = (radius_to - radius_from) / ms
        # 细粒度20ms
        for i in range(self.time_step, ms, self.time_step):
            self.sleep_ms(self.time_step)
            self._press_move(0, center_x - (radius_from + x_step * i), center_y, 100)
            self._press_move(1, center_x + (radius_from + x_step * i), center_y, 100)
        # 最后一步
        self.sleep_ms(ms % self.time_step)
        self._press_move(0, center_x - radius_to, center_y, 100)
        self._press_move(1, center_x + radius_to, center_y, 100)
        self._press_up(0)
        self._press_up(1)
