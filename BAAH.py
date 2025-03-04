import sys
import os

# 将当前脚本所在目录添加到模块搜索路径
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)

from modules.utils.log_utils import logging
from modules.configs.MyConfig import config
from modules.utils import *
from modules.AllTask.myAllTask import my_AllTask

def print_BAAH_info():
    print("+" + "BAAH".center(80, "="), "+")
    print("||" + f"Version: {config.softwareconfigdict['NOWVERSION']}".center(80, " ") + "||")
    print("||" + "Bilibili: https://space.bilibili.com/7331920".center(80, " ") + "||")
    print("||" + "Github: https://github.com/sanmusen214/BAAH".center(80, " ") + "||")
    print("||" + "QQ group: 441069156".center(80, " ") + "||")
    print("||" + "".center(80, " ") + "||")
    print("+" + "".center(80, "=") + "+")

def print_BAAH_start():
    print_BAAH_info()
    # 打印config信息
    logging.info({"zh_CN": f"读取的配置文件: {config.nowuserconfigname}", "en_US": f"Read config file: {config.nowuserconfigname}"})
    logging.info({"zh_CN": f"模拟器:{config.userconfigdict['TARGET_EMULATOR_PATH']}",
                    "en_US":f"Emulator: {config.userconfigdict['TARGET_EMULATOR_PATH']}"})
    logging.info({"zh_CN": f"端口:{config.userconfigdict['TARGET_PORT']}",
                    "en_US": f"Port: {config.userconfigdict['TARGET_PORT']}"})
    logging.info({"zh_CN": f"区服:{config.userconfigdict['SERVER_TYPE']}",
                    "en_US": f"Server: {config.userconfigdict['SERVER_TYPE']}"})
    

def print_BAAH_finish():
    print_BAAH_info()
    print("\n程序运行结束，如有问题请加群(441069156)反馈，在Github上检查下是否有版本更新")
    print("https://github.com/sanmusen214/BAAH")

def BAAH_release_adb_port(justDoIt=False):
    """
    释放adb端口，通常被一个后台进程占用
    """
    if config.userconfigdict["KILL_PORT_IF_EXIST"] or justDoIt:
        try:
            # 确保端口未被占用
            res = subprocess_run(["netstat", "-ano"], encoding="gbk").stdout
            for line in res.split("\n"):
                if ":"+str(config.userconfigdict["TARGET_PORT"]) in line and "LISTENING" in line:
                    logging.info(line)
                    logging.info({"zh_CN":"端口被占用，正在释放" , "en_US":"Port is used, releasing now"})
                    pid=line.split()[-1]
                    subprocess_run(["taskkill", "/T", "/F", "/PID", pid], encoding="gbk")
                    logging.info({"zh_CN": "端口被占用，已释放", "en_US": "Port is used, released"})
                    config.sessiondict["PORT_IS_USED"] = True
                    break
        except Exception as e:
            logging.error({"zh_CN": "释放端口失败，请关闭模拟器后重试",
                           "en_US": "Failed to release port, please close the emulator and try again"})
            logging.error(e)


def _check_process_exist(pid):
    """
    检查进程是否存在
    """
    try:
        tasks = subprocess_run(["tasklist"], encoding="gbk").stdout
        tasklist = tasks.split("\n")
        for task in tasklist:
            wordlist = task.strip().split()
            if len(wordlist) > 1 and wordlist[1] == str(pid):
                logging.info(" | ".join(wordlist))
                return True
        return False
    except Exception as e:
        logging.error(e)
        return False


def BAAH_start_emulator():
    """
    启动模拟器
    """
    if config.userconfigdict["TARGET_EMULATOR_PATH"] and config.userconfigdict["TARGET_EMULATOR_PATH"] != "":
        try:
            # 以列表形式传命令行参数
            logging.info({"zh_CN": "启动模拟器", "en_US": "Starting the emulator"})
            emulator_process = subprocess_run(config.userconfigdict['TARGET_EMULATOR_PATH'].split(" "), isasync=True)
            logging.info({"zh_CN": "模拟器pid: " + str(emulator_process.pid),
                          "en_US": "The emulator pid: " + str(emulator_process.pid)})
            time.sleep(5)
            # 检查pid是否存在
            if not _check_process_exist(emulator_process.pid):
                logging.warn({"zh_CN": "模拟器启动进程已结束，可能是启动失败，或者是模拟器已经在运行",
                              "en_US": "The emulator startup process has ended, may be startup failed, or the emulator is already running"})
            else:
                # 存进session，这样最后根据需要按照这个pid杀掉模拟器
                config.sessiondict["EMULATOR_PROCESS_PID"] = emulator_process.pid
        except Exception as e:
            logging.error({"zh_CN": "启动模拟器失败, 可能是没有以管理员模式运行 或 配置的模拟器路径有误",
                           "en_US": "Failed to start the emulator, maybe not run as administrator or the emulator path is wrong"})
            logging.error(e)
    else:
        logging.info({"zh_CN": "未配置模拟器路径，跳过启动模拟器",
                      "en_US": "No emulator path configured, skip starting the emulator"})


def BAAH_check_adb_connect():
    """
    检查adb连接
    """
    # 检查adb连接
    disconnect_this_device()
    for i in range(1, 10):
        sleep(i)
        if check_connect():
            logging.info({"zh_CN": "adb连接成功", "en_US": "Adb connected successfully"})
            return True
        else:
            logging.info({"zh_CN": "未检测到设备连接, 重试...", "en_US": "Could not detect device connection, retrying..."})
    if config.sessiondict["PORT_IS_USED"]:
        # 连接失败，并且出现端口被占用的情况，现在模拟器的用户可见进程的端口估计是配置文件里的后一个端口
        # 提醒用户启动BAAH时，不要启动模拟器
        raise Exception("检测到启动BAAH前 端口已被占用，但BAAH无法连接至该端口。上次模拟器可能未被正常关闭，请在启动BAAH前关闭模拟器")
    raise Exception("adb连接失败, 请检查配置里的adb端口")


def BAAH_start_VPN():
    """
    启动加速器
    """
    if config.userconfigdict["USE_VPN"]:
        logging.info({"zh_CN": "启动指定的加速器", "en_US": "Starting the specified accelerator"})
        try:
            if config.userconfigdict['VPN_CONFIG']['VPN_ACTIVITY']:
                open_app(config.userconfigdict['VPN_CONFIG']['VPN_ACTIVITY'])
            sleep(5)
            logging.info({"zh_CN": f"当前打开的应用: {get_now_running_app()}",
                          "en_US": f"now running app: {get_now_running_app()}"})
            # 点击
            for click_sleep_pair in config.userconfigdict['VPN_CONFIG']['CLICK_AND_WAIT_LIST']:
                screenshot()
                click_pos, sleep_time = click_sleep_pair
                # 如果为列表且第一个元素为负数，表示不点击
                if type(click_pos) == list and click_pos[0] < 0 and click_pos[1] < 0:
                    if sleep_time > 0:
                        sleep(sleep_time)
                    continue
                logging.info({"zh_CN": f"点击{click_pos}, 等待{sleep_time}秒",
                              "en_US": f"Cilck {click_pos}, wait {sleep_time} seconds"})
                print(type(sleep_time))
                click(click_pos, sleeptime=sleep_time)
        except Exception as e:
            logging.error({"zh_CN": "启动加速器失败, 可能是配置有误",
                           "en_US": "Accelerator failed to start, possibly due to misconfiguration"})
            logging.error(e)
    else:
        logging.info({"zh_CN": "跳过启动加速器", "en_US": "Skip startup accelerator"})


def BAAH_open_target_app():
    """
    打开游戏
    """
    # logging.info({"zh_CN": "先关闭游戏", "en_US": "Detected that the game is already running"})
    # close_app(config.userconfigdict['ACTIVITY_PATH'])
    # if check_app_running(config.userconfigdict['ACTIVITY_PATH']):
    #     logging.info({"zh_CN": "检测到游戏已经在运行", "en_US": "Detected that the game is already running"})
    #     return True
    for i in range(40):
        logging.info({"zh_CN": f"打开游戏{i}/30", "en_US": f"Try to open the game {i}/30"})
        open_app(config.userconfigdict['ACTIVITY_PATH'])
        sleep(3)
        if not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
            logging.error({"zh_CN": "未检测到游戏打开，请检查区服设置",
                           "en_US": "No game detected, please check the server settings"})
        else:
            return True
    raise Exception("未检测到游戏打开，请检查区服设置 以及 如果使用的是MuMu模拟器，请关闭后台保活")

def BAAH_run_pre_command():
    if len(config.userconfigdict["PRE_COMMAND"]) > 0:
        logging.info({"zh_CN": "运行前置命令", "en_US": "Running pre command"})
        sleep(1.5)
        subprocess.Popen(config.userconfigdict["PRE_COMMAND"], shell=True)

def BAAH_run_post_command():
    if len(config.userconfigdict["POST_COMMAND"]) > 0:
        logging.info({"zh_CN": "运行后置命令", "en_US": "Running post command"})
        sleep(1.5)
        subprocess.Popen(config.userconfigdict["POST_COMMAND"], shell=True)

def BAAH_kill_emulator():
    """
    杀掉模拟器的用户可见窗口进程
    """
    if (config.userconfigdict["TARGET_EMULATOR_PATH"] and
            config.userconfigdict["TARGET_EMULATOR_PATH"] != "" and config.userconfigdict["CLOSE_EMULATOR_BAAH"]):
        try:
            if not config.sessiondict["EMULATOR_PROCESS_PID"]:
                logging.error({"zh_CN": "未能获取到模拟器进程，跳过关闭模拟器",
                               "en_US": "Failed to get the emulator process, skip closing the emulator"})
                return
            # 提取出模拟器的exe名字
            full_path = config.userconfigdict['TARGET_EMULATOR_PATH']
            emulator_exe = os.path.basename(full_path).split(".exe")[0] + ".exe"
            subprocess_run(["taskkill", "/T", "/F", "/PID", str(config.sessiondict["EMULATOR_PROCESS_PID"])],
                           encoding="gbk")
            # 杀掉模拟器可见窗口进程后，可能残留后台进程，这里根据adb端口再杀一次
            BAAH_release_adb_port(justDoIt=True)
        except Exception as e:
            logging.error({"zh_CN": "关闭模拟器失败, 可能是没有以管理员模式运行 或 配置的模拟器路径有误",
                           "en_US": "Failed to close the emulator, "
                                    "maybe not run as administrator or the emulator path is wrong"})
            logging.error(e)
    else:
        logging.info({"zh_CN": "跳过关闭模拟器", "en_US": "Skip closing the emulator"})


def BAAH_send_email():
    """
    发送邮件
    """
    logging.info({"zh_CN": "尝试发送通知", "en_US": "Trying to send notification"})
    try:
        # 构造通知对象
        notificationer = create_notificationer()
        # 构造邮件内容
        content = []
        content.append("BAAH任务结束")
        content.append("配置文件名称: " + config.nowuserconfigname)
        content.append("任务开始时间: " + config.sessiondict["BAAH_START_TIME"])
        content.append("开始时资源: " + str(config.sessiondict["BEFORE_BAAH_SOURCES"]))
        content.append("任务结束时间: " + time.strftime("%Y-%m-%d %H:%M:%S"))
        content.append("结束时资源: " + str(config.sessiondict["AFTER_BAAH_SOURCES"]))
        content.append("游戏区服: " + config.userconfigdict["SERVER_TYPE"])
        # 任务内容
        content.append("执行的任务内容:")
        tasks_str = ""
        for ind, task in enumerate(config.userconfigdict["TASK_ORDER"]):
            if config.userconfigdict["TASK_ACTIVATE"][ind]:
                tasks_str += f" -> {task}"
        content.append(tasks_str)
        # 其他消息
        content.append("其他消息:")
        info_str = ""
        # INFO_DICT 和 INFO_LIST 里的信息
        for key, value in config.sessiondict["INFO_DICT"].items():
            info_str += f"{value}\n"
        for info in config.sessiondict["INFO_LIST"]:
            info_str += f"{info}\n"
        content.append(info_str)
        # 发送
        notificationer.send("\n".join(content))
        logging.info({"zh_CN": "通知发送结束", "en_US": "Finished sending notification"})
    except Exception as e:
        logging.error({"zh_CN": "发送通知失败", "en_US": "Failed to send notification"})
        logging.error(e)

def BAAH_auto_quit(forcewait = False):
    """ 结束运行，如果用户没有勾选自动关闭模拟器与BAAH，等待用户按回车键 """
    # 用于GUI识别是否结束的关键字
    print("GUI_BAAH_TASK_END")
    # if forcewait or not config.userconfigdict["CLOSE_EMULATOR_BAAH"]:
    #     input("Press Enter to exit/回车退出:")
    # else:
    logging.info({"zh_CN": "10秒后自动关闭", "en_US": "Auto close in 10 seconds"})
    sleep(10)
        
def BAAH_rm_pic():
    """运行结束后，删除截图文件，内含try-except"""
    try:
        # 运行结束后如果截图文件存在，删除截图文件
        if os.path.exists(f"./{config.userconfigdict.get('SCREENSHOT_NAME')}"):
            os.remove(f"./{config.userconfigdict.get('SCREENSHOT_NAME')}")
    except Exception as e:
        logging.error({"zh_CN": "删除截图文件失败", "en_US": "Failed to delete screenshot file"})

def BAAH_send_err_mail(e):
    """ 发送错误通知邮件 """
    if config.userconfigdict["ENABLE_MAIL_NOTI"]:
        logging.info({"zh_CN": "发送错误通知邮件", "en_US": "Send error notification email"})
        try:
            # 构造通知对象
            notificationer = create_notificationer()
            # 构造邮件内容
            content = []
            content.append("BAAH任务出现错误")
            content.append("配置文件名称: " + config.nowuserconfigname)
            content.append("游戏区服: " + config.userconfigdict["SERVER_TYPE"])
            content.append("错误信息: " + str(e))
            print(notificationer.send("\n".join(content)))
            logging.info({"zh_CN": "邮件发送结束", "en_US": "The email has been sent"})
        except Exception as eagain:
            logging.error({"zh_CN": "发送邮件失败", "en_US": "Failed to send email"})
            logging.error(eagain)

def BAAH_main():
    """
    执行BAAH主程序，在此之前config应该已经被单独import然后解析为用户指定的配置文件->随后再导入my_AllTask以及其他依赖config的模块
    """
    try:
        # TODO: 加任务执行前后bash脚本
        config.sessiondict["BAAH_START_TIME"] = time.strftime("%Y-%m-%d %H:%M:%S")
        print_BAAH_start()
        BAAH_run_pre_command()
        BAAH_release_adb_port()
        BAAH_start_emulator()
        BAAH_check_adb_connect()
        BAAH_start_VPN()
        BAAH_open_target_app()
        
        # 运行任务
        logging.info({"zh_CN": "运行任务", "en_US": "start running tasks"})
        my_AllTask.run()
        logging.info({"zh_CN": "所有任务结束", "en_US": "All tasks are finished"})
        BAAH_kill_emulator()
        BAAH_send_email()
        print_BAAH_finish()
        BAAH_rm_pic()
        BAAH_run_post_command()
        
        BAAH_auto_quit()

        
    except Exception as e:
        logging.error({"zh_CN": "运行出错", "en_US": "Error occurred"})
        # 打印完整的错误信息
        import traceback
        traceback.print_exc()
        BAAH_send_err_mail(e)
        print_BAAH_finish()
        BAAH_auto_quit(forcewait=True)


if __name__ in ["__main__", "__mp_main__"]:
    # 不带GUI运行
    BAAH_main()