from nicegui import ui

def set_cafe(config):
    with ui.row():
        ui.link_target("CAFE")
        ui.label(config.get_text("task_cafe")).style('font-size: x-large')
    
    ui.label(config.get_text("config_cafe_attention"))
    
    with ui.row():
        ui.checkbox(config.get_text("cafe_collect_desc")).bind_value(config.userconfigdict, "CAFE_COLLECT")
        
    with ui.row():
        ui.checkbox(config.get_text("cafe_touch_desc")).bind_value(config.userconfigdict, "CAFE_TOUCH")
        full_camera = ui.checkbox(config.get_text("config_camera_full")).bind_value(config.userconfigdict, "CAFE_CAMERA_FULL").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        full_camera.set_value(True)
        full_camera.set_enabled(False)
        ui.checkbox(config.get_text("enable_diff_touch")).bind_value(config.userconfigdict, "CAFE_TOUCH_WAY_DIFF").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        
    with ui.row():
        ui.checkbox(config.get_text("cafe_invite_desc")).bind_value(config.userconfigdict, "CAFE_INVITE").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        ui.checkbox(config.get_text("cafe_invite_desc1")).bind_value(config.userconfigdict, "CAFE_INVITE1").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        ui.checkbox(config.get_text("cafe_invite_desc2")).bind_value(config.userconfigdict, "CAFE_INVITE2").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")