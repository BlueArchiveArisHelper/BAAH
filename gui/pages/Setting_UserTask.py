from nicegui import ui
from gui.components.cut_screenshot import test_screencut

def set_usertask(config, parsed_obj_dict):
    with ui.row():
        ui.link_target("USER_DEF_TASK")
        ui.label(config.get_text("task_user_def_task")).style('font-size: x-large')
    
    # 是否开启操作actions flow group模式
    ui.checkbox(config.get_text("flow_mode")).bind_value(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK")

    with ui.row():
        with ui.column().bind_visibility_from(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK", backward=lambda x:x):
            ui.button("测试截图/screencut test", on_click=lambda: test_screencut(config))
            flow_group = parsed_obj_dict.get("OBJ_USER_DEFINE_TASK", None)
            flow_group.render_gui(config)


        ui.textarea(label = config.get_text("task_user_def_task")).bind_value(config.userconfigdict, "USER_DEF_TASKS").style('width: 40vw;').bind_visibility_from(config.userconfigdict, "USE_OBJ_USER_DEFINE_TASK", backward=lambda x:not x)