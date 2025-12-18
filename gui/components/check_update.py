from ..define import gui_shared_config

from nicegui import ui, run
import time
import requests
import os
from datetime import datetime
from update import whether_has_new_version

g_result = None
g_datetime = ""

def only_check_version():
    """
    确保缓存机制在第一次触发该函数时生效，如果已经有多个打开的页面，可能会在启动时导致多次请求。（不过现在的实现方式导致只有一个页面能获取api查询结果）
    """
    global g_result, g_datetime
    datetime_now = datetime.now().strftime("%Y-%m-%d %H")
    # 缓存判断日期，如果日期相同就不用再次请求
    if datetime_now == g_datetime and g_result is not None:
        print(f"Use cached release info: {datetime_now}")
        return g_result
    # 缓存判断后
    g_datetime = datetime_now # 更新缓存判断值
    # ==请求最新版本信息==
    g_result = whether_has_new_version()
    return g_result
