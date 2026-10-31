from nicegui import ui, run
import platform
from define_actions import FlowActionGroup
from gui.components.cut_screenshot import test_screencut
from modules.configs.MyConfig import config as glconfig
from modules.configs.multiserverSettings import is_server_type_in_group, MultiServerType
from modules.utils import connect_to_device, get_now_running_app,  get_now_running_app_entrance_activity, screen_shot_to_global

def set_vpn(config, parsed_obj_dict):
    with ui.row():
        ui.link_target("VPN")
        ui.label(config.get_text("setting_vpn")).style('font-size: x-large')

    # 根据电脑系统决定是否导入win32包
    if platform.system() == "Windows":
        from modules.utils.win32_utils import _get_hwnd, check_esc_is_pressed, capture_program_window_precise, click_program_window_precise, scroll_program_window_precise
        def enter_PC_APP_edit_mode():
            config.sessiondict["AUTO_CONTROL_PC_WINDOW_NAME"] = False
            config.sessiondict["CONTROL_PC_WINDOW_NAME"] = config.userconfigdict["PC_GAME_ACC_WINDOW_NAME"]
        def quit_PC_APP_edit_mode():
            config.sessiondict["AUTO_CONTROL_PC_WINDOW_NAME"] = True
        def track_ACC_WINDOW_NAME(e, cfg):
            # print(f"Changed in GUI: {e.value}")
            cfg.userconfigdict["PC_GAME_ACC_WINDOW_NAME"] = e.value
            cfg.sessiondict["CONTROL_PC_WINDOW_NAME"] = e.value
        # 根据区服决定是否显示PC端加速器按钮
        with ui.column().bind_visibility_from(config.userconfigdict, "SERVER_TYPE", backward = lambda x:is_server_type_in_group(x, MultiServerType.PCGroup)):
            # 填入PC上加速器相关参数 PC_GAME_ACC_WINDOW_NAME
            ui.input("加速器程序窗口名", value = config.userconfigdict["PC_GAME_ACC_WINDOW_NAME"], on_change=lambda e: track_ACC_WINDOW_NAME(e, config))
            ui.button("进入加速器截图模式", on_click=enter_PC_APP_edit_mode, color="orange").bind_visibility_from(config.sessiondict, "AUTO_CONTROL_PC_WINDOW_NAME")
            ui.button("退出加速器截图模式", on_click=quit_PC_APP_edit_mode, color="green").bind_visibility_from(config.sessiondict, "AUTO_CONTROL_PC_WINDOW_NAME", backward=lambda x: not x)


    # -----------------------------
    # 选择是否定义 开加速器 actions
    ui.checkbox(config.get_text("vpn_desc")).bind_value(config.userconfigdict, "USE_VPN")
    start_group:FlowActionGroup = parsed_obj_dict["OBJ_ACTIONS_VPN_START"]
    start_group.render_gui(config)
    # -----------------------------
    ui.separator()
    # 选择是否定义 关闭加速器 actions
    ui.checkbox(config.get_text("vpn_stop_desc")).bind_value(config.userconfigdict, "CLOSE_VPN")
    end_group:FlowActionGroup = parsed_obj_dict["OBJ_ACTIONS_VPN_SHUT"]
    end_group.render_gui(config)
    # -----------------------------
