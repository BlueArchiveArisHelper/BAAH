import subprocess
import sys
import os
import logging
import psutil
from typing import Tuple

logging.getLogger("subprocess").setLevel(logging.WARNING)

def subprocess_run(cmd: Tuple[str]|str, isasync=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, encoding = "utf-8", shell=False, **kwargs):
    """
    Run a command in a subprocess and return the instance.
    If encoding is set, no need to encode/decode the input/output when dealing with text.
    
    Parameters
    ==========
    cmd: list|str
        The command to run.
        
    Returns
    =======
    pipeline
    """
    # https://www.cnblogs.com/superbaby11/p/16195273.html
    # shell 为True时，cmd可以是字符串，否则是列表。列表的第一个元素是命令，后面的元素是传递给shell的参数。
    if isasync:
        # 异步非阻塞执行
        return subprocess.Popen(cmd, stdout=stdout, stderr=stderr, stdin=stdin, encoding=encoding, shell=shell, **kwargs)
    else:
        # 同步阻塞执行
        return subprocess.run(cmd, stdout=stdout, stderr=stderr, stdin=stdin, encoding=encoding, shell=shell, **kwargs)
    
def check_if_process_exist(key_name, key_value):
    """ 检查是否有 key_name 包含 key_value 的进程们 """
    result_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        if key_value in proc.info[key_name]:
            result_list.append(proc)
    return result_list