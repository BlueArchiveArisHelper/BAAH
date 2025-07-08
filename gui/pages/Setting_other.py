from nicegui import ui, run
from gui.components.cut_screenshot import cut_screenshot
from gui.components.list_edit_area import list_edit_area
import os
import subprocess
import time

from modules.utils import screencut_tool, connect_to_device, screen_shot_to_global

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

    with ui.row():
        # IP+端口
        ui.input(config.get_text("config_ip_root")).bind_value(config.userconfigdict, 'TARGET_IP_PATH',forward=lambda v: v.replace("\\", "/")).style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: not v)
        
        # 序列号
        ui.input(config.get_text("adb_serial")).bind_value(config.userconfigdict, 'ADB_SEIAL_NUMBER').style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)
        
        # 切换使用序列号还是IP+端口
        ui.checkbox(config.get_text("adb_direct_use_serial")).bind_value(config.userconfigdict, 'ADB_DIRECT_USE_SERIAL_NUMBER')
    
    with ui.row():
        ui.checkbox(config.get_text("config_physics")).bind_value(config.userconfigdict, 'CONFIG_PHYSICS').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)
    
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
    
    async def test_screencut():
        await cut_screenshot(
            inconfig=config,
            left_click=True,
            right_click=True,
            quick_return=False
            )
    
    # 将截图功能内嵌进GUI
    with ui.row():
        ui.button("测试截图/screencut test", on_click=test_screencut)

    async def restart_adb_server():
        subprocess.run([config.userconfigdict['ADB_PATH'], "kill-server"])
        time.sleep(0.5)
        subprocess.run([config.userconfigdict['ADB_PATH'], "start-server"])
        print("adb server restarted")
        ui.notify("adb server resstarted")

    # adb kill-server
    with ui.row():
        ui.button(config.get_text("button_kill_adb_server"), on_click=restart_adb_server, color="red")