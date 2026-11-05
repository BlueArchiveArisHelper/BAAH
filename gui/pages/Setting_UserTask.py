from nicegui import ui
from gui.components.cut_screenshot import test_screencut
from gui.components.modern_ui import info_tip

def set_usertask(config, parsed_obj_dict):
    # 是否开启操作actions flow group模式
    ui.checkbox(config.get_text("flow_mode")).bind_value(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK")

    with ui.row():
        with ui.column().bind_visibility_from(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK", backward=lambda x:x):
            flow_group = parsed_obj_dict.get("OBJ_USER_DEFINE_TASK", None)
            flow_group.render_gui(config)


        with info_tip(config, "tip_python_code") as row:
            row.bind_visibility_from(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK", backward=lambda x:not x)
            ui.textarea(label = config.get_text("config_python_code")).bind_value(config.userconfigdict, "USER_DEF_TASKS").style('width: 40vw;')