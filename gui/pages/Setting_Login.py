from nicegui import ui
from gui.components.cut_screenshot import test_screencut
from gui.components.modern_ui import info_tip


def set_login(config, parsed_obj_dict):
    # 是否在登录页面执行用户OBJ FLOW脚本
    with info_tip(config, "tip_flow_when_login_game"):
        ui.checkbox(config.get_text("desc_flow_when_login_game")).bind_value(config.userconfigdict, 'USE_OBJ_FLOW_WHEN_LOGIN')

    # 登录页面的OBJ FLOW脚本
    with ui.row().bind_visibility_from(config.userconfigdict, 'USE_OBJ_FLOW_WHEN_LOGIN'):
        flow_group = parsed_obj_dict.get("OBJ_FLOW_WHEN_LOGIN", None)
        flow_group.render_gui(config)
