def handle_error_mention(e, print_method):
    """
    根据各种奇妙的异常字符串，给出异常解决提示

    无论是完整process运行还是单个函数运行，出异常后都会调用这个函数
    """
    try:
        print_method("=================")
        print_method(f"错误提示: {e}")
        print_method(f"Error Mention: {e}")
        if "EOF" in e:
            print_method("错误提示(EOF): 如果手动出击队伍的话，请使用终端执行推走格子图任务！")
            print_method("Error Mention(EOF): If you wanna manually select teams, please use terminal to run the grid quest explore task!")
    except Exception as newe:
        print("Error when mention error msg: " + str(newe))

def BAAH_core_process(reread_config_name = None, must_auto_quit = False, msg_queue = None):
    """
    运行BAAH核心流程
    RUN CORE BAAH PROCESS

    @param reread_config_name: 是否重新解析config名
    @param must_auto_quit: 是否运行结束时自动退出
    @param msg_queue: log输出管道
    """
    # ============= Initialize =============
    from modules.configs.MyConfig import config
    if reread_config_name is not None:
        config.parse_user_config(reread_config_name)
    
    from modules.utils.log_utils import logging
    logging.set_log_queue(msg_queue)

    # ============= Import =============

    import os
    from modules.utils import subprocess_run, time, disconnect_this_device, sleep, check_connect, check_shizuku, set_dpi ,set_wm_size, reset_dpi, reset_wm_size, open_app, close_app, get_now_running_app, screenshot, click, check_app_running, subprocess, create_notificationer, EmulatorBlockError, istr, EN, CN
    from modules.AllTask.myAllTask import my_AllTask

    def print_BAAH_info():
        logging.info("+" + "BAAH".center(80, "=") + "+")
        logging.info("||" + f"Version: {config.softwareconfigdict['NOWVERSION']}".center(80, " ") + "||")
        logging.info("||" + "Bilibili: https://space.bilibili.com/7331920".center(80, " ") + "||")
        logging.info("||" + "Github: https://github.com/sanmusen214/BAAH".center(80, " ") + "||")
        logging.info("||" + "QQ group: 715586983".center(80, " ") + "||")
        logging.info("||" + "".center(80, " ") + "||")
        logging.info("+" + "".center(80, "=") + "+")

    def print_BAAH_config_info():
        adb_connect_string = f"{config.userconfigdict['ADB_SEIAL_NUMBER']}" if config.userconfigdict['ADB_DIRECT_USE_SERIAL_NUMBER'] else f"{config.userconfigdict['TARGET_IP_PATH']}:{config.userconfigdict['TARGET_PORT']}"
        # 打印config信息
        logging.info({"zh_CN": f"读取的配置文件: {config.nowuserconfigname}", "en_US": f"Read config file: {config.nowuserconfigname}"})
        logging.info({"zh_CN": f"模拟器:{config.userconfigdict['TARGET_EMULATOR_PATH']}",
                        "en_US":f"Emulator: {config.userconfigdict['TARGET_EMULATOR_PATH']}"})
        logging.info({"zh_CN": f"ADB连接: {adb_connect_string}",
                        "en_US": f"ADB connect: {adb_connect_string}"})
        logging.info({"zh_CN": f"区服:{config.userconfigdict['SERVER_TYPE']}",
                        "en_US": f"Server: {config.userconfigdict['SERVER_TYPE']}"})
        

    def print_BAAH_finish():
        print_BAAH_info()
        logging.info("\n程序运行结束，如有问题请反馈，在Github上检查下是否有版本更新")
        logging.info("https://github.com/sanmusen214/BAAH")

    def BAAH_release_adb_port(justDoIt=False):
        """
        释放adb端口，通常被一个后台进程占用
        """
        if config.userconfigdict["KILL_PORT_IF_EXIST"] or justDoIt:
            try:
                # 确保端口未被占用
                res = subprocess_run(["netstat", "-ano"], encoding=None, text=True).stdout
                for line in res.split("\n"):
                    if ":"+str(config.userconfigdict["TARGET_PORT"]) in line and "LISTENING" in line:
                        logging.info(line)
                        logging.info({"zh_CN":"端口被占用，正在释放" , "en_US":"Port is used, releasing now"})
                        pid=line.split()[-1]
                        subprocess_run(["taskkill", "/T", "/F", "/PID", pid], encoding=None)
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
            # encoding使用None，使用text指定获取str结果
            tasks = subprocess_run(["tasklist"], encoding=None, text=True).stdout
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
                # 不能用shell，否则得到的是shell的pid
                emulator_process = subprocess_run(config.userconfigdict['TARGET_EMULATOR_PATH'], isasync=True)
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
        # shizuku断联会假死，AVD/实体机断联会连不上，已经连接不会多出<devices>:5555的设备  --BlockHaity
        if config.userconfigdict["CONFIG_PHYSICS"] is False:
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

    def _do_user_defined_action(activity_name, action_list):
        """执行用户定义的点击坐标或图片序列"""
        try:
            if activity_name:
                open_app(activity_name)
            sleep(5)
            logging.info({"zh_CN": f"当前打开的应用: {get_now_running_app()}",
                        "en_US": f"now running app: {get_now_running_app()}"})
            # 点击
            for click_sleep_pair in action_list:
                screenshot()
                click_pos, sleep_time = click_sleep_pair
                # 如果为列表且第一个元素为负数，表示不点击
                if type(click_pos) == list and click_pos[0] < 0 and click_pos[1] < 0:
                    if sleep_time > 0:
                        sleep(sleep_time)
                    continue
                logging.info({"zh_CN": f"点击{click_pos}, 等待{sleep_time}秒",
                            "en_US": f"Cilck {click_pos}, wait {sleep_time} seconds"})
                logging.info(type(sleep_time))
                click(click_pos, sleeptime=sleep_time)
        except Exception as e:
            logging.error({"zh_CN": "执行用户定义序列失败, 可能是配置有误",
                        "en_US": "Failed to preform user-defined actions, possibly due to misconfiguration"})
            logging.error(e)

    def BAAH_start_VPN():
        """
        启动加速器
        """
        if config.userconfigdict["USE_VPN"]:
            logging.info({"zh_CN": "启动指定的加速器", "en_US": "Starting the specified accelerator"})
            _do_user_defined_action(
                activity_name=config.userconfigdict['VPN_CONFIG']['VPN_ACTIVITY'],
                action_list=config.userconfigdict['VPN_CONFIG']['CLICK_AND_WAIT_LIST']
            )
        else:
            logging.info({"zh_CN": "跳过启动加速器", "en_US": "Skip startup accelerator"})
    
    def BAAH_close_VPN():
        """
        关闭加速器
        """
        if config.userconfigdict["CLOSE_VPN"]:
            logging.info({"zh_CN": "关闭指定的加速器", "en_US": "Stop the specified accelerator"})
            _do_user_defined_action(
                activity_name=config.userconfigdict['VPN_CLOSE_CONFIG']['VPN_ACTIVITY'],
                action_list=config.userconfigdict['VPN_CLOSE_CONFIG']['CLICK_AND_WAIT_LIST']
            )
        else:
            logging.info({"zh_CN": "跳过关闭加速器", "en_US": "Skip stop accelerator"})


    def BAAH_open_target_app():
        """
        打开游戏
        """
        if check_app_running(config.userconfigdict['ACTIVITY_PATH']):
            logging.info({"zh_CN": "检测到游戏已经在运行", "en_US": "Detected that the game is already running"})
            return True
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

    def BAAH_close_target_app(must_do=False, meet_error=False):
        """
        关闭游戏
        """
        if ((not meet_error and config.userconfigdict["CLOSE_GAME_FINISH"]) or must_do or (meet_error and config.userconfigdict["CLOSE_GAME_ERROR"])):
            if not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
                logging.info({"zh_CN": "检测到游戏已关闭", "en_US": "Detected that the game is already killing"})
                return True
            for i in range(5):
                logging.info({"zh_CN": f"关闭游戏{i}/5", "en_US": f"Try to close the game {i}/5"})
                close_app(config.userconfigdict['ACTIVITY_PATH'])
                sleep(3)
                if not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
                    logging.info({"zh_CN": "游戏已关闭", "en_US": "Game is already killing"})
                    return True
                    
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

    def BAAH_kill_emulator(must_do = False, meet_error = False):
        """
        杀掉模拟器进程
        """
        if (config.userconfigdict["TARGET_EMULATOR_PATH"] and 
            ((not meet_error and config.userconfigdict["CLOSE_EMULATOR_FINISH"]) 
             or 
             must_do
             or
             (meet_error and config.userconfigdict["CLOSE_EMULATOR_ERROR"]))
             ):
            try:
                if not config.sessiondict["EMULATOR_PROCESS_PID"]:
                    logging.error({"zh_CN": "未能获取到模拟器进程，跳过关闭模拟器",
                                "en_US": "Failed to get the emulator process, skip closing the emulator"})
                    return
                # 提取出模拟器的exe名字
                full_path = config.userconfigdict['TARGET_EMULATOR_PATH']
                emulator_exe = os.path.basename(full_path).split(".exe")[0] + ".exe"
                subprocess_run(["taskkill", "/T", "/F", "/PID", str(config.sessiondict["EMULATOR_PROCESS_PID"])],
                            encoding=None)
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
            content.append(istr({
                CN: "BAAH任务结束",
                EN: "BAAH Finished"
            }))
            content.append(istr({
                CN: "配置文件名称: " + config.nowuserconfigname,
                EN: "Config name: " + config.nowuserconfigname
            }))
            
            content.append(istr({
                CN: "任务开始时间: " + config.sessiondict["BAAH_START_TIME"],
                EN: "Task start at: " + config.sessiondict["BAAH_START_TIME"],
            }))
            content.append(istr({
                CN: "开始时资源: " + str(config.sessiondict["BEFORE_BAAH_SOURCES"]),
                EN: "Resource at start: " + str(config.sessiondict["BEFORE_BAAH_SOURCES"])
            }))
            content.append(istr({
                CN: "任务结束时间: " + time.strftime("%Y-%m-%d %H:%M:%S"),
                EN: "Task finish at: " + time.strftime("%Y-%m-%d %H:%M:%S")
            }))
            content.append(istr({
                CN: "结束时资源: " + str(config.sessiondict["AFTER_BAAH_SOURCES"]),
                EN: "Resource in the end: " + str(config.sessiondict["AFTER_BAAH_SOURCES"])
            }))
            content.append(istr({
                CN: "游戏区服: " + config.userconfigdict["SERVER_TYPE"],
                EN: "Game server: " + config.userconfigdict["SERVER_TYPE"]
            }))
            # 任务内容
            content.append(istr({
                CN: "执行的任务内容:",
                EN: "Task completed: "
            }))
            tasks_str = ""
            for ind, task in enumerate(config.userconfigdict["TASK_ORDER"]):
                if config.userconfigdict["TASK_ACTIVATE"][ind]:
                    tasks_str += f" -> {task}"
            content.append(tasks_str)
            # 其他消息
            content.append(istr({
                CN: "其他消息:",
                EN: "Other messages"
            }))
            info_str = ""
            # INFO_DICT 里的信息
            for key, value in config.sessiondict["INFO_DICT"].items():
                info_str += f"{value}\n"
            content.append(info_str)
            # 发送
            fullcontent = "\r\n".join(content)
            notificationer.send(fullcontent, title=istr({CN: "BAAH结束", EN: "BAAH finished"}))
            logging.info({"zh_CN": "通知发送结束", "en_US": "Finished sending notification"})
        except Exception as e:
            logging.error({"zh_CN": "发送通知失败", "en_US": "Failed to send notification"})
            logging.error(e)

    def BAAH_auto_quit(key_map_func = None, meet_error = False):
        """ 结束运行，如果用户没有勾选自动关闭模拟器与BAAH，等待用户按回车键 """
        # 默认值空字典
        if key_map_func is None:
            key_map_func = dict()
        if must_auto_quit:
            return
        if (
            (not meet_error and config.userconfigdict["CLOSE_BAAH_FINISH"])
            or
            (meet_error and config.userconfigdict["CLOSE_BAAH_ERROR"])
            ):
            logging.info({"zh_CN": "10秒后自动关闭", "en_US": "Auto close in 10 seconds"})
            sleep(10)
        else:
            user_input = input(f"Press Enter to exit/回车退出, "+str([f"[{k}]{key_map_func[k]['desc']}" for k in key_map_func]) + ": ")
            for k in key_map_func:
                if user_input.upper() == k.upper():
                    key_map_func[k]["func"]()
                    break
            
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
                content.append(istr({
                    CN: "BAAH任务错误",
                    EN: "BAAH Error"
                }))
                content.append(istr({
                    CN: "配置文件名称: " + config.nowuserconfigname,
                    EN: "Config Name: " + config.nowuserconfigname,
                }))
                content.append(istr({
                    CN: "游戏区服: " + config.userconfigdict["SERVER_TYPE"],
                    EN: "Game server: " + config.userconfigdict["SERVER_TYPE"],
                }))
                content.append(istr({
                    CN: "错误信息: " + str(e),
                    EN: "Error Message: " + str(e),
                }))
                logging.info(notificationer.send("\n".join(content), title=istr({CN: "BAAH任务失败", EN: "BAAH Error"})))
                logging.info({"zh_CN": "邮件发送结束", "en_US": "The email has been sent"})
            except Exception as eagain:
                logging.error({"zh_CN": "发送邮件失败", "en_US": "Failed to send email"})
                logging.error(eagain)

    def BAAH_physical_start():
        """物理机开头操作"""
        if check_shizuku() is True:
            logging.warn({"zh_CN": "检测到shizuku,Android Termux支持为实验性支持，建议使用mumu模拟器运行BAAH"})
        set_dpi("240")
        set_wm_size([1280, 720])
    
    def BAAH_physical_end():
        """物理机结尾操作"""
        reset_dpi()
        reset_wm_size()
    
    def BAAH_main(run_precommand = True):
        """
        执行BAAH主程序, 在此之前config应该已经被单独import然后解析为用户指定的配置文件->随后再导入my_AllTask以及其他依赖config的模块
        """
        try:
            # 同级别的except只能捕获同级别的try里的错误
            try:
                config.sessiondict["BAAH_START_TIME"] = time.strftime("%Y-%m-%d %H:%M:%S")
                print_BAAH_info()
                print_BAAH_config_info()
                if run_precommand:
                    BAAH_run_pre_command()
                if config.userconfigdict["CONFIG_PHYSICS"] is False:
                    BAAH_release_adb_port()
                    BAAH_start_emulator()
                BAAH_check_adb_connect()
                if config.userconfigdict["CONFIG_PHYSICS"] is True:
                    BAAH_physical_start()
                BAAH_start_VPN()
                BAAH_open_target_app()
                
                # 运行任务
                logging.info({"zh_CN": "运行任务", "en_US": "start running tasks"})
                my_AllTask.run()
                logging.info({"zh_CN": "所有任务结束", "en_US": "All tasks are finished"})
                BAAH_close_target_app()
                BAAH_close_VPN()
                if config.userconfigdict["CONFIG_PHYSICS"] is True:
                    BAAH_physical_end()
                if config.userconfigdict["CONFIG_PHYSICS"] is False:
                    BAAH_kill_emulator()
                BAAH_send_email()
                print_BAAH_finish()
                BAAH_rm_pic()
                BAAH_run_post_command()
                
                print_BAAH_config_info()
                BAAH_auto_quit()

            except EmulatorBlockError as ebe:
                logging.info(istr({
                    CN: "模拟器卡顿，重启模拟器",
                    EN: "Emulator Blocked, Restart Emulator"
                }))
                if config.sessiondict["EMULATOR_PROCESS_PID"] is None:
                    logging.error(istr({
                        CN: "无模拟器pid，无法重启模拟器，请确保模拟器由BAAH启动",
                        EN: "Cannot identify emulator's pid, fail to restart emulator, please make sure it is started by BAAH"
                    }))
                # sessionstorage里重启次数加1
                store_restart_times = config.sessiondict["RESTART_EMULATOR_TIMES"] + 1
                logging.info(istr({
                    CN: "关闭应用",
                    EN: "Close the app"
                }))
                BAAH_close_target_app(must_do=True)
                logging.info(istr({
                    CN: "关闭模拟器",
                    EN: "Close the emulator"
                }))
                BAAH_kill_emulator(must_do=True)
                logging.info(istr({
                    CN: "重新运行脚本",
                    EN: "Restart the script"
                }))
                time.sleep(5)
                # 重新加载其他config值，覆盖模拟器重启次数到sessiondict
                config.parse_user_config(config.nowuserconfigname)
                config.sessiondict["RESTART_EMULATOR_TIMES"] = store_restart_times
                # 防止重复调用precommand
                BAAH_main(run_precommand=False)

        # 最外层的except捕获正常运行过程中的错误 以及 模拟器重启次数达到最大值的错误
        except Exception as e:
            logging.error({"zh_CN": f"运行出错: {e}", "en_US": f"Error occurred: {e}"})
            # 打印完整的错误信息
            import traceback
            # 打印错误信息, 保存日志信息到文件
            detailed_trackback_str = traceback.format_exc()
            logging.error(detailed_trackback_str)
            handle_error_mention(str(e), logging.warn)
            logging.save_custom_log_file()
            # 发送错误邮件
            BAAH_send_err_mail(e)
            # 关闭游戏和模拟器
            BAAH_close_target_app(meet_error=True)
            BAAH_kill_emulator(meet_error=True)
            print_BAAH_finish()
            
            print_BAAH_config_info()
            def continue_redo_tasks():
                """出错后用户选择从出错点继续执行脚本"""
                # 记录CURRENT_PERIOD_TASK_INDEX
                last_period_task_index = config.sessiondict["CURRENT_PERIOD_TASK_INDEX"]
                # 重新加载其他config值
                config.parse_user_config(config.nowuserconfigname)
                # 重新加载CURRENT_PERIOD_TASK_INDEX
                config.sessiondict["CURRENT_PERIOD_TASK_INDEX"] = last_period_task_index
                # 执行BAAH
                BAAH_main(run_precommand=False)
            
            BAAH_auto_quit(key_map_func={
                "R": {
                    "desc":"estart", # [R]estart
                    "func":lambda: [config.parse_user_config(config.nowuserconfigname), BAAH_main()]
                      },
                "C": {
                    "desc":"ontinue", # [C]ontinue
                    "func":continue_redo_tasks
                }
            }, meet_error=True)


    # Run
    BAAH_main()


def BAAH_single_func_process(reread_config_name = None, msg_queue = None, to_run_func_config_name = None):
    """
    快捷执行某一个函数的wrapped方法
    """
    if to_run_func_config_name is None:
        raise Exception("to_run_func_config_name is None")
    
    # ============= Initialize =============
    from modules.configs.MyConfig import config
    if reread_config_name is not None:
        config.parse_user_config(reread_config_name)
    
    from modules.utils.log_utils import logging
    logging.set_log_queue(msg_queue)

    # ============= Import =============

    from modules.utils import check_connect, istr, EN, CN
    from modules.AllTask.myAllTask import task_instances_map

    if to_run_func_config_name not in task_instances_map.taskmap:
        raise Exception(f"to_run_func_config_name: {to_run_func_config_name} not in task_instances_map.taskmap")
    
    # 执行
    try:
        print("to_run_func_config_name: ", to_run_func_config_name)
        task_ins = task_instances_map.taskmap[to_run_func_config_name]
        module_func = task_ins.task_module
        params_func = task_ins.task_params
        check_connect()
        module_func(**params_func).run()
    except Exception as e:
        logging.error({"zh_CN": f"运行出错: {e}", "en_US": f"Error occurred: {e}"})
        # 打印完整的错误信息
        import traceback
        # 打印错误信息
        detailed_trackback_str = traceback.format_exc()
        logging.error(detailed_trackback_str)
        handle_error_mention(str(e), logging.warn)