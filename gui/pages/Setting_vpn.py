from nicegui import ui, run
from define_actions import FlowActionGroup
from modules.configs.MyConfig import config as glconfig

def set_vpn(config, parsed_obj_dict):
    with ui.row():
        ui.link_target("VPN")
        ui.label(config.get_text("setting_vpn")).style('font-size: x-large')

    # -----------------------------
    # 选择是否定义 开加速器 actions
    with ui.card():
        ui.checkbox(config.get_text("vpn_desc")).bind_value(config.userconfigdict, "USE_VPN")
        group:FlowActionGroup = parsed_obj_dict["OBJ_ACTIONS_VPN_START"]
        group.render_gui(config)


    # fag = FlowActionGroup()
    # fag.render_gui(config)
    glconfig.parse_user_config(config.nowuserconfigname)
    ui.button("Show", on_click=lambda: print(group.to_json_dict()))
    ui.button("Run", on_click=lambda: group.run_flow())