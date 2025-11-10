import sys
import os


def run_baah_script(config_name):
    try:
        from modules.utils.log_utils import logging
        # 从命令行参数获取要运行的config文件名，并将config实例parse为那个config文件
        from modules.configs.MyConfig import config

        logging.info({"zh_CN": f"当前运行目录: {os.getcwd()}", "en_US": f"Current running directory: {os.getcwd()}"})
        now_config_files = config.get_all_user_config_names()
        logging.info({"zh_CN": "BAAH_CONFIGS可用的配置文件: " + ", ".join(now_config_files), "en_US": "Available BAAH_CONFIGS config files: " + ", ".join(now_config_files)})
        for i in range(len(now_config_files)):
            logging.info(f"{i}: {now_config_files[i]}")

        if config_name is not None:
            logging.info({"zh_CN": f"读取指定的配置文件: {config_name}", "en_US": f"loading config from {config_name}"})
            if config_name not in now_config_files:
                logging.error({"zh_CN": "输入的配置文件名不在可用配置文件列表中", "en_US": "The entered config file name is not in the list of available config files"})
                raise FileNotFoundError(f"Config file {config_name} not found")

            config.parse_user_config(config_name)
        else:
            logging.warn({"zh_CN": "启动程序时没有指定配置文件,启动时请设置如 'BAAH.exe ceshi.json' 启动参数", "en_US": "No config file specified when starting the program, please use 'BAAH.exe configname' to declare config name"})
            raise Exception("No config file specified")
        # 按照该配置文件，运行BAAH
        # 加载my_AllTask，BAAH_main，create_notificationer
        # 以这时的config构建任务列表
        from BAAH import BAAH_core_process

        # 不带GUI运行
        BAAH_core_process()
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Error, Enter to exit/错误，回车退出:")
