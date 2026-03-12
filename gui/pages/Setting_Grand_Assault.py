from nicegui import ui
from gui.components.cut_screenshot import cut_screenshot, screencut_button

def set_grand_assault(config):
    with ui.row():
        ui.link_target("grand_ASSAULT")
        ui.label(config.get_text("task_grand_assault")).style('font-size: x-large')
    
    ui.label(config.get_text("desc_grand_assault"))
    
    ui.label('1:"Normal", 2:"Hard", 3:"Very Hard", 4: "Hardcore", 5: "Extreme", 6: "Insane", 7: "Torment"')
    # 分为左中右三个填写框
    with ui.row():
        ui.number(config.get_text("desc_grand_assault_left_level"),
            min=1,
            max=7,
            precision=0,
            step=1
        ).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_LEFT_LEVEL", forward=lambda x: int(x)).style("width: 100px")
        ui.number(config.get_text("desc_grand_assault_middle_level"),
            min=1,
            max=7,
            precision=0,
            step=1
        ).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_MIDDLE_LEVEL", forward=lambda x: int(x)).style("width: 100px")
        ui.number(config.get_text("desc_grand_assault_right_level"),
            min=1,
            max=7,
            precision=0,
            step=1
        ).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_RIGHT_LEVEL", forward=lambda x: int(x)).style("width: 100px")

    ui.checkbox(config.get_text("desc_grand_assault_no_fight")).bind_value(config.userconfigdict, "GRAND_ASSAULT_NO_FIGHT")
    ui.checkbox(config.get_text("error_if_grand_assault_no_team")).bind_value(config.userconfigdict, "GRAND_ASSAULT_NO_TEAM_EXCEPT")