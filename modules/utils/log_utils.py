import sys
import os
from time import strftime
# !在解析config之前导入log_utils的话，config可能未解析userconfigdict，避免使用userconfigdict，只使用softwareconfigdict
from modules.configs.MyConfig import config
from modules.utils.I18nstr import istr, EN, CN, JP

import hashlib

# 构建日志类
class MyLogger:
    """
    日志类，包装常用的日志类方法，info, debug, warn, warning, error
    """
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARN = "WARN"
    ERROR = "ERROR"
    
    def __init__(self) -> None:
        self.custom_log_list = []
        self.info_list = []
        self.debug_list = []
        self.warn_list = []
        self.error_list = []
        self.lang = config.softwareconfigdict["LANGUAGE"]
        self.logqueue = None
        print("Use language: ", self.lang)
        self.tick = False
        self.logfile = None

    def get_now_time_str(self):
        return strftime("%Y-%m-%d-%H-%M-%S")

    def tick_log_file_fd(self):
        """
        创建log文件fd，同一生命周期内只会创建一次
        """
        try:
            if self.tick:
                # 第一次尝试logging内容的时候创建fd，后面再触发不需要再创建
                return
            self.tick = True
            # 使用softwareconfigdict的配置来决定是否保存log到文件
            if config.softwareconfigdict["SAVE_LOG_TO_FILE"]:
                now_timestr = self.get_now_time_str()
                log_file_full_path = os.path.join(config.LOG_FOLDER, f"log_{now_timestr}.txt")
                self.logfile = open(log_file_full_path, "w", encoding="utf-8")
                print(f"track log file fd, log output to: {log_file_full_path}")
            else:
                self.logfile = None
                print("track log file switch off")
        except Exception as e:
            print(f"Create log file error: {e}")
            import traceback
            traceback.print_exc()
            self.logfile = None

    def save_custom_log_file(self, path=None, name=None):
        """
        保存发生了错误的全量custom日志到文件
        """
        if self.custom_log_list:
            try:
                now_timestr = self.get_now_time_str()
                file_short_name = f"custom_log_{now_timestr}.txt"
                if path is not None and name is not None:
                    file_full_path = os.path.join(path, name)
                else:
                    file_full_path = os.path.join(config.LOG_FOLDER, file_short_name)
                with open(file_full_path, "w", encoding="utf-8") as f:
                    for line in self.custom_log_list:
                        f.write(line + "\n")
                logging.info("↓↓↓↓↓↓↓↓↓↓")
                logging.info(self.get_i18n_sentence({
                    CN: f"保存全量异常日志到文件: {file_full_path}",
                    EN: f"Save full custom log to file: {file_full_path}"
                }))
                logging.info("↑↑↑↑↑↑↑↑↑↑")
            except Exception as e:
                logging.error(self.get_i18n_sentence({
                    CN: f"保存全量异常日志到文件失败: {e}",
                    EN: f"Save full custom log to file failed: {e}"
                }))
                import traceback
                traceback.print_exc()

    # def save_custom_log_file_for_crash_report(self, path, now_timestr):
    #     """
    #     保存发生了错误的全量custom日志到文件,为崩溃报告专用
    #     """
    #     if self.custom_log_list:
    #         try:
    #             file_short_name = f"custom_log_{now_timestr}.txt"
    #             file_full_path = os.path.join(config.LOG_FOLDER, file_short_name)
    #             with open(file_full_path, "w", encoding="utf-8") as f:
    #                 for line in self.custom_log_list:
    #                     f.write(line + "\n")
    #             #  导出一份到错误报告目录下
    #             with open(path + "/error.log", "w", encoding="utf-8") as f:
    #                 for line in self.custom_log_list:
    #                     f.write(line + "\n")
    #             logging.info("↓↓↓↓↓↓↓↓↓↓")
    #             logging.info(self.get_i18n_sentence({
    #                 CN: f"保存全量异常日志到文件: {file_full_path}和错误报告目录下",
    #                 EN: f"Save full custom log to file: {file_full_path}"
    #             }))
    #             logging.info("↑↑↑↑↑↑↑↑↑↑")
    #         except Exception as e:
    #             logging.error(self.get_i18n_sentence({
    #                 CN: f"保存全量异常日志到文件失败: {e}",
    #                 EN: f"Save full custom log to file failed: {e}"
    #             }))
    #             import traceback
    #             traceback.print_exc()

    # 析构函数
    def __del__(self):
        if self.logfile:
            self.logfile.close()
            self.logfile = None
    
    def set_log_queue(self, queue):
        self.logqueue = queue
        
    def hash_str(self, data):
        """得到字符串的哈希值"""
        return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()
    
    def get_i18n_sentence(self, msg):
        """从dict中得到当前i18n语言"""
        if isinstance(msg, dict):
            if self.lang in msg:
                msg = msg[self.lang]
            else:
                # 没有对应语言的情况下，使用英文
                # 目前EN = "en_US"，与传入的json的代表英语的key是对应的
                if EN in msg:
                    msg = msg[EN]
        return msg

    def format_msg(self, msg, level):
        """解析dict或str，加入时间，错误级别"""
        msg = self.get_i18n_sentence(msg)
        output_line = f"{config.NOWVERSION} - {strftime('%M:%S')} - {level} : {str(msg)}"
        return output_line
    
    def colorful_print(self, msg, level):
        """
        30 黑色，31 红色，32 绿色，33 黄色，34 蓝色，35 紫色，36 青色，37 白色
        
        cmd 用不了
        """
        # if level == self.INFO:
        #     print(f"\033[1;32m{msg}\033[0m")
        # elif level == self.DEBUG:
        #     print(f"\033[1;34m{msg}\033[0m")
        # elif level == self.WARN:
        #     print(f"\033[1;33m{msg}\033[0m")
        # elif level == self.ERROR:
        #     print(f"\033[1;31m{msg}\033[0m")
        # else:
        #     print(msg)
        print(msg)
        # 打印出来的东西都保存到常规log file里
        self.tick_log_file_fd()
        if self.logfile:
            try:
                self.logfile.write(msg + "\n")
                self.logfile.flush()
            except Exception as e:
                print(f"log file exception: {e}")
                self.logfile = None
        if self.logqueue:
            try:
                self.logqueue.put_nowait(msg)
            except Exception as e:
                print(f"log queue exception: {e}")
                self.logqueue = None
        # flush
        sys.stdout.flush()
        
    
    def info(self, msg):
        formatted_msg = self.format_msg(msg, self.INFO)
        self.info_list.append(formatted_msg)
        self.custom_log_list.append(formatted_msg)
        self.colorful_print(formatted_msg, self.INFO)
    
    def debug(self, msg):
        formatted_msg = self.format_msg(msg, self.DEBUG)
        self.debug_list.append(formatted_msg)
        # debug只保存到custom log里，不打印也不保存到常规log里
        self.custom_log_list.append(formatted_msg)
        # self.colorful_print(formatted_msg, self.DEBUG)
    
    def warn(self, msg):
        formatted_msg = self.format_msg(msg, self.WARN)
        self.warn_list.append(formatted_msg)
        self.custom_log_list.append(formatted_msg)
        self.colorful_print(formatted_msg, self.WARN)
    
    def warning(self, msg):
        self.warn(msg)
        
    def error(self, msg):
        formatted_msg = self.format_msg(msg, self.ERROR)
        self.error_list.append(formatted_msg)
        self.custom_log_list.append(formatted_msg)
        self.colorful_print(formatted_msg, self.ERROR)
    
logging = MyLogger()