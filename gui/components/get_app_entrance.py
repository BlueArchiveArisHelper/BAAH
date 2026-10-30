from modules.utils import *
from nicegui import ui
from .modern_ui import form_row

def connect_and_get_now_app(useconfig, resultdict, resultkey, enter_activity = True):
    """
    链接并获取当前运行的app
    """
    if not useconfig:
        useconfig = config
    connect_to_device(useconfig)
    appstr = ""
    if enter_activity:
        appstr = get_now_running_app_entrance_activity(useconfig)
    else:
        appstr = get_now_running_app(useconfig)
    resultdict[resultkey] = appstr
    return appstr


def get_app_entrance_button(inconfig, resultdict, resultkey, input_text="Package"):
    # 应用路径及获取按钮共用可换行布局，保持既有参数回填。
    with form_row():
        ui.input(input_text).bind_value(resultdict, resultkey).style("width: 300px")
        ui.button(inconfig.get_text("button_get_now_app_enter"), on_click=lambda: connect_and_get_now_app(useconfig=inconfig, resultdict=resultdict, resultkey=resultkey, enter_activity=True))
        ui.button(inconfig.get_text("button_get_now_app"), on_click=lambda: connect_and_get_now_app(useconfig=inconfig, resultdict=resultdict, resultkey=resultkey, enter_activity=False))


    