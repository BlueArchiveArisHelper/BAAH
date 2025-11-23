from nicegui import ui
from gui.components.cut_screenshot import test_screencut


def set_login(config, parsed_obj_dict):
    with ui.row():
        # ui.link_target("LOGINGAME")
        ui.label(config.get_text("task_login_game")).style('font-size: x-large')
    
    # 是否在登录页面执行用户OBJ FLOW脚本
    ui.checkbox(config.get_text("desc_flow_when_login_game")).bind_value(config.userconfigdict, 'USE_OBJ_FLOW_WHEN_LOGIN')

    # 登录页面的OBJ FLOW脚本
    with ui.row().bind_visibility_from(config.userconfigdict, 'USE_OBJ_FLOW_WHEN_LOGIN'):
        flow_group = parsed_obj_dict.get("OBJ_FLOW_WHEN_LOGIN", None)
        flow_group.render_gui(config)

    # 截图测试
    ui.separator()
    with ui.row():
        ui.button("测试截图/screencut test", on_click=lambda: test_screencut(config))