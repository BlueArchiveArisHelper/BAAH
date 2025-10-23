from nicegui import ui, run
from define_actions import FlowActionGroup
from gui.components.cut_screenshot import test_screencut
from modules.configs.MyConfig import config as glconfig
from modules.utils import connect_to_device, get_now_running_app,  get_now_running_app_entrance_activity, screen_shot_to_global

def set_vpn(config, parsed_obj_dict):
    with ui.row():
        ui.link_target("VPN")
        ui.label(config.get_text("setting_vpn")).style('font-size: x-large')

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

    # 将截图功能内嵌进GUI
    ui.separator()
    with ui.row():
        ui.button("测试截图/screencut test", on_click=lambda: test_screencut(config))