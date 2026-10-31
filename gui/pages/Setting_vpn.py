from nicegui import ui
import platform
from define_actions import FlowActionGroup
from gui.components.modern_ui import setting_group, form_row, operation_bar
from modules.configs.multiserverSettings import is_server_type_in_group, MultiServerType
from modules.utils import enter_PC_APP_edit_mode, quit_PC_APP_edit_mode

def set_vpn(config, parsed_obj_dict):
    with ui.row():
        ui.link_target("VPN")
        ui.label(config.get_text("setting_vpn")).classes('baah-section-title')

    # PC 窗口设置复用公共分组，保留原有区服显隐与模式切换回调。
    if platform.system() == "Windows":
        def track_ACC_WINDOW_NAME(e, cfg):
            """当用户在加速界面修改加速器窗口名的时候，需要将其保存到配置文件中 并且 实时同步到sessiondict以便即使已经在自由PC软件截图模式也能变更控制窗口名"""
            cfg.userconfigdict["PC_GAME_ACC_WINDOW_NAME"] = e.value
            cfg.sessiondict["CONTROL_PC_WINDOW_NAME"] = e.value
        # 根据区服决定是否显示PC端加速器按钮
        with setting_group(config.get_text("config_pc_accelerator")) as pc_group:
            pc_group.bind_visibility_from(config.userconfigdict, "SERVER_TYPE", backward=lambda x: is_server_type_in_group(x, MultiServerType.PCGroup))
            # 填入PC上加速器相关参数 PC_GAME_ACC_WINDOW_NAME
            with form_row():
                ui.input(config.get_text("config_pc_acc_window_name"), value=config.userconfigdict["PC_GAME_ACC_WINDOW_NAME"], on_change=lambda e: track_ACC_WINDOW_NAME(e, config)).classes('w-full')
            with operation_bar():
                ui.button(config.get_text("button_enter_pc_acc_mode"), icon="crop", on_click=lambda cfg=config: enter_PC_APP_edit_mode(cfg), color="warning").bind_visibility_from(config.sessiondict, "AUTO_CONTROL_PC_WINDOW_NAME")
                ui.button(config.get_text("button_quit_pc_acc_mode"), icon="exit_to_app", on_click=lambda cfg=config: quit_PC_APP_edit_mode(cfg), color="positive").bind_visibility_from(config.sessiondict, "AUTO_CONTROL_PC_WINDOW_NAME", backward=lambda x: not x)


    # -----------------------------
    # 选择是否定义 开加速器 actions
    with setting_group(config.get_text("config_vpn_start_actions")):
        ui.checkbox(config.get_text("vpn_desc")).bind_value(config.userconfigdict, "USE_VPN")
        start_group:FlowActionGroup = parsed_obj_dict["OBJ_ACTIONS_VPN_START"]
        start_group.render_gui(config)
    # -----------------------------
    # 选择是否定义 关闭加速器 actions
    with setting_group(config.get_text("config_vpn_stop_actions")):
        ui.checkbox(config.get_text("vpn_stop_desc")).bind_value(config.userconfigdict, "CLOSE_VPN")
        end_group:FlowActionGroup = parsed_obj_dict["OBJ_ACTIONS_VPN_SHUT"]
        end_group.render_gui(config)
    # -----------------------------
