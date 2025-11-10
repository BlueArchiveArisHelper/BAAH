from nicegui import ui
from gui.components.cut_screenshot import cut_screenshot, screencut_button

def set_assault(config):
    with ui.row():
        ui.link_target("ASSAULT")
        ui.label(config.get_text("task_assault")).style('font-size: x-large')
    
    ui.label(config.get_text("desc_assault"))
    
    ui.label('1:"Normal", 2:"Hard", 3:"Very Hard", 4: "Hardcore", 5: "Extreme", 6: "Insane", 7: "Torment"')
    ui.number(
        "",
        min=1,
        precision=0,
        step=1
    ).bind_value(config.userconfigdict, "AUTO_ASSAULT_LEVEL", forward=lambda x: int(x)).style("width: 100px")
    
    ui.checkbox(config.get_text("error_if_assault_no_team")).bind_value(config.userconfigdict, "ASSAULT_NO_TEAM_EXCEPT")

    # 是否自动配队
    # ui.checkbox(config.get_text("config_auto_team")).bind_value(config.userconfigdict, "IS_AUTO_ASSAULT_AUTO_TEAM")
    
    # 是否助战
    ui.checkbox(config.get_text("config_need_assault_helper")).bind_value(config.userconfigdict, "IS_AUTO_ASSAULT_STUDENT_HELP")
    with ui.column().bind_visibility_from(config.userconfigdict, "IS_AUTO_ASSAULT_STUDENT_HELP"):
        # 助战是否后排
        ui.checkbox(config.get_text("config_assault_helper_is_support")).bind_value(config.userconfigdict, "AUTO_ASSAULT_HELP_STUDENT_IS_SUPPORT")
        
        screencut_button(inconfig=config, resultdict=config.userconfigdict, resultkey="AUTO_ASSAULT_HELP_STUDENT", input_text=config.get_text("config_assault_helper_student"), button_text=config.get_text("config_assault_helper_student"))