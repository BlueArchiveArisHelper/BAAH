import sys
import os
from time import sleep, strftime

# 将当前脚本所在目录添加到模块搜索路径
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)


if __name__ in ["__main__", "__mp_main__"]:
    try:
        # config logging before all imports
        from modules.utils.log_utils import logging
        # 从命令行参数获取要运行的config文件名，并将config实例parse为那个config文件
        from modules.configs.MyConfig import config

        if len(sys.argv) > 1:
            config_name = sys.argv[1]
            logging.info({"zh_CN": f"读取指定的配置文件: {config_name}", "en_US": f"loading config from {config_name}"})
            config.parse_user_config(config_name)
        else:
            logging.warn({"zh_CN": "启动程序时没有指定配置文件", "en_US": "No config file specified when starting the program"})
            now_config_files = config.get_all_user_config_names()
            logging.info({"zh_CN": "可用的配置文件: " + ", ".join(now_config_files), "en_US": "Available config files: " + ", ".join(now_config_files)})
            if len(now_config_files) == 1:
                logging.info({"zh_CN": "自动读取唯一的配置文件", "en_US": "Automatically read the only config file"})
                config_name = now_config_files[0]
            else:
                while(1):
                    logging.info({"zh_CN": "请手动输入要运行的配置文件名(包含.json后缀)", "en_US": "Please enter the config file name to run (including .json suffix)"})
                    config_name = input(": ")
                    if config_name in now_config_files:
                        break
                    else:
                        logging.warn({"zh_CN": "输入的配置文件名不在可用配置文件列表中", "en_US": "The entered config file name is not in the list of available config files"})
            logging.info({"zh_CN": f"读取指定的配置文件: {config_name}", "en_US": f"loading config from {config_name}"})
            config.parse_user_config(config_name)
        # 按照该配置文件，运行BAAH
        # 加载my_AllTask，BAAH_main，create_notificationer
        # 以这时的config构建任务列表
        from BAAH import BAAH_main, my_AllTask, create_notificationer

        # 不带GUI运行
        BAAH_main()
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 用于GUI识别是否结束的关键字
        print("GUI_BAAH_TASK_END")
        # input("Error, Enter to exit/错误，回车退出:")
