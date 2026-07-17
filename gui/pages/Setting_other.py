from nicegui import ui, run
import cv2
from gui.components.cut_screenshot import cut_screenshot, test_screencut
from gui.components.list_edit_area import list_edit_area
import os
import subprocess
import time

from DATA.assets.ButtonName import ButtonName
from DATA.assets.PageName import PageName
from DATA.assets.PopupName import PopupName
from modules.utils import screencut_tool, connect_to_device, screen_shot_to_global, button_pic, popup_pic, page_pic, match_pattern,screenshot,get_config_adb_path,getNewestSeialNumber,subprocess_run

def set_other(config, gui_shared_config):
    with ui.row():
        ui.link_target("TOOL_PATH")
        ui.label(config.get_text("setting_other")).style('font-size: x-large')

    ui.label("BAAH Settings").style('font-size: x-large')
    
    with ui.row():
        # 日志保存
        ui.checkbox(config.get_text("config_output_log")).bind_value(gui_shared_config.softwareconfigdict, 'SAVE_LOG_TO_FILE')
    
    with ui.row():
        # 异常日志保存
        ui.checkbox(config.get_text("config_output_err_log")).bind_value(gui_shared_config.softwareconfigdict, 'SAVE_ERR_CUSTOM_LOG')
    
    with ui.row():
        # 错误报告
        ui.checkbox(config.get_text("config_crash_report")).bind_value(gui_shared_config.softwareconfigdict, "ENABLE_CRASH_REPORT")
    
    with ui.row():
        ui.number(config.get_text("config_run_until_try_times"),
                  step=1,
                  min=3,
                  precision=0).bind_value(config.userconfigdict, 'RUN_UNTIL_TRY_TIMES', forward=lambda x:int(x), backward=lambda x:int(x))
        
    with ui.row():
        ui.number(config.get_text("config_run_until_wait_time"),
                  suffix="s",
                  step=0.1,
                  min=0.1,
                  precision=1
                  ).bind_value(config.userconfigdict, 'RUN_UNTIL_WAIT_TIME')
    
    with ui.row():
        ui.number(config.get_text("config_wait_time_after_click"),
                    suffix="s",
                    step=0.1,
                    precision=1).bind_value(config.userconfigdict, 'TIME_AFTER_CLICK')
    
    ui.label(config.get_text("config_desc_response_y"))
    with ui.row():
        ui.number(config.get_text("config_response_y"),
                    step=1,
                    min=1,
                    precision=0).bind_value(config.userconfigdict, 'RESPOND_Y', forward=lambda x:int(x), backward=lambda x:int(x)).bind_enabled(config.userconfigdict, 'LOCK_SERVER_TO_RESPOND_Y', forward=lambda v: not v, backward=lambda v: not v)
        ui.checkbox(config.get_text("config_bind_response_to_server")).bind_value(config.userconfigdict, 'LOCK_SERVER_TO_RESPOND_Y')
    
    with ui.row():
        # 截图模式
        ui.select(options=["png", "pipe"], label=config.get_text("config_screenshot_mode")).bind_value(config.userconfigdict, 'SCREENSHOT_METHOD').style('width: 400px')

    ui.label(config.get_text("config_warn_change")).style('color: red')

    # with ui.row():
    #     # IP+端口
    #     ui.input(config.get_text("config_ip_root")).bind_value(config.userconfigdict, 'TARGET_IP_PATH',forward=lambda v: v.replace("\\", "/")).style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: not v)
        
    #     # 序列号
    #     ui.input(config.get_text("adb_serial")).bind_value(config.userconfigdict, 'ADB_SEIAL_NUMBER').style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)
        
    #     # 切换使用序列号还是IP+端口
    #     ui.checkbox(config.get_text("adb_direct_use_serial")).bind_value(config.userconfigdict, 'ADB_DIRECT_USE_SERIAL_NUMBER')
    
    with ui.row():
        ui.input(config.get_text("config_adb_path")).bind_value(config.userconfigdict, 'ADB_PATH',forward=lambda v: v.replace("\\", "/")).style('width: 400px')

    
    with ui.row():
        ui.input(config.get_text("config_screenshot_name")).bind_value(config.userconfigdict, 'SCREENSHOT_NAME',forward=lambda v: v.replace("\\", "/")).style('width: 400px').set_enabled(False)
    
    # 测试/开发使用
    # 检查当前文件夹下有没有screencut.exe文件
    # whethercut = os.path.exists("./screencut.exe")
    # if whethercut:
    #     with ui.row():
    #         ui.button("测试截图/screencut test", on_click=lambda: os.system(f'start screencut.exe "{load_jsonname}"'))

    with ui.row():
        ui.input(config.get_text("aria2_path")).bind_value(config.userconfigdict, 'ARIA2_PATH',forward=lambda v: v.replace("\\", "/")).style('width: 400px')
    
    with ui.row():
        ui.number(config.get_text("aria2_thread"),
                  step=1,
                  min=1,
                  precision=0).bind_value(config.userconfigdict, 'ARIA2_THREADS', forward=lambda x: int(x) if x is not None else 0, backward=lambda x: int(x) if x is not None else 0)
    
    with ui.row():
        ui.number(config.get_text("aria2_max_tries"),
                  step=1,
                  min=1,
                  precision=0).bind_value(config.userconfigdict, 'ARIA2_MAX_TRIES', forward=lambda x: int(x) if x is not None else 0, backward=lambda x: int(x) if x is not None else 0)   

    with ui.row():
        ui.number(config.get_text("aria2_failured_wait_time"),
                  suffix="s",
                  step=0.1,
                  min=0.1,
                  precision=1
                  ).bind_value(config.userconfigdict, 'ARIA2_FAILURED_WAIT_TIME')
    
    ui.label("Test").style('font-size: x-large')
    
    # 将截图功能内嵌进GUI
    with ui.row():
        ui.button(config.get_text("text_screenshot"), on_click=lambda: test_screencut(config))

    async def restart_adb_server():
        subprocess.run([config.userconfigdict['ADB_PATH'], "kill-server"])
        time.sleep(0.5)
        subprocess.run([config.userconfigdict['ADB_PATH'], "start-server"])
        print("adb server restarted")
        ui.notify("adb server resstarted")

    # adb kill-server
    with ui.row():
        ui.button(config.get_text("button_kill_adb_server"), on_click=restart_adb_server, color="red")

    # 测试图片识别按钮
    pic_path_dict = {
        "button":{
            "func": lambda name, c=config: button_pic(name, use_config=c),
            "list": [k for k in ButtonName.__dict__.keys() if not k.startswith("__")]
        },
        "page":{
            "func": lambda name, c=config: page_pic(name, use_config=c),
            "list": [k for k in PageName.__dict__.keys() if not k.startswith("__")]
        },
        "popup":{
            "func": lambda name, c=config: popup_pic(name, use_config=c),
            "list": [k for k in PopupName.__dict__.keys() if not k.startswith("__")]
        }
    }
    now_focus_pic_type = {
        "typename": "button",
        "filename": pic_path_dict["button"]["list"][0]
    }
    @ui.refreshable
    def show_quick_pic_match():
        def update_big_type(e):
            now_focus_pic_type["typename"] = e.value
            now_focus_pic_type["filename"] = pic_path_dict[e.value]["list"][0]
            show_quick_pic_match.refresh()
        def update_small_name(e):
            now_focus_pic_type["filename"] = e.value
            show_quick_pic_match.refresh()
        def screencut_and_match():
            connect_to_device(use_config = config)
            screen_shot_to_global(use_config = config, output_png = True)
            match_pattern(cv2.imread(config.userconfigdict['SCREENSHOT_NAME']), pic_path_dict[now_focus_pic_type["typename"]]["func"](now_focus_pic_type["filename"]), show_result=True, auto_rotate_if_trans=False)
        with ui.row():
            with ui.column():
                ui.select(list(pic_path_dict.keys()), on_change=update_big_type, value=now_focus_pic_type["typename"]).style('width: 200px')
            
            with ui.column():
                ui.select(list(pic_path_dict[now_focus_pic_type["typename"]]["list"]), on_change=update_small_name, value=now_focus_pic_type["filename"]).style('width: 200px')
            
            with ui.column():
                ui.button("GO!", on_click=screencut_and_match)



    show_quick_pic_match()

    # 测试亮度调整
    def query_brightness():
        connect_to_device(config)
        res = subprocess_run([get_config_adb_path(config), "-s", getNewestSeialNumber(config), "shell", "settings", "get", "system", "screen_brightness"], text=True)
        print("Now brightness is: "+res.stdout)
        ui.notify(res.stdout)
    brightness_number = {"val": 21}
    with ui.row():
        ui.button("查询亮度/Query", on_click=query_brightness)
        ui.number("亮度/Brightness", step=1, min=0, precision=0).bind_value(brightness_number, 'val', forward=lambda x:int(x), backward=lambda x:int(x))
        ui.button("设置/Set", on_click=lambda: [
            connect_to_device(config),
            subprocess_run([get_config_adb_path(config), "-s", getNewestSeialNumber(config), "shell", "settings", "put", "system", "screen_brightness", str(brightness_number["val"])]), 
            ui.notify("Done")
            ])