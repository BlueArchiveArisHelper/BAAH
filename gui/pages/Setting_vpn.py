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
        # 根据区服决定是否显示PC端加速器按钮
        if is_server_type_in_group(config, MultiServerType.PCGroup):
            # 填入PC上加速器相关参数 PC_GAME_ACC_WINDOW_NAME，PC_GAME_ACC_EXE_PATH
            ui.input("The window name of acc exe").bind_value(config.userconfigdict, "PC_GAME_ACC_WINDOW_NAME")
            ui.input("The path of acc exe").bind_value(config.userconfigdict, "PC_GAME_ACC_EXE_PATH")

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
