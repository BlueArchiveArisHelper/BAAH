from nicegui import ui
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName

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

def set_quick_runtask(config, real_taskname_to_show_taskname, logArea):
    
    # 快速调用任务
    show_fast_run_task_buttons([
        TaskName.MOMOTALK, 
        [TaskName.MAIN_STORY, TaskName.MAIN_SECOND_STORY, TaskName.SHORT_STORY, TaskName.SIDE_STORY],
        TaskName.SOLVE_CHALLENGE, 
        [TaskName.PUSH_NORMAL, TaskName.PUSH_HARD],
        [TaskName.EVENTPUSHSTORYQUEST, TaskName.EVENTRECAP]
    ], config, real_taskname_to_show_taskname, logArea)

    ui.splitter(horizontal=True)
    # ========================
    # 调试相关
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