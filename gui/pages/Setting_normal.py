from nicegui import ui
from gui.components.edit_team_strength import edit_the_team_strength_of_this_config
from gui.components.list_edit_area import list_edit_area

def set_normal(config):
    
    with ui.row():
        ui.link_target("NORMAL")
        ui.label(config.get_text("task_normal")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_times"))
    ui.switch(config.get_text("config_event_status")).bind_value(config.userconfigdict, "NORMAL_QUEST_EVENT_STATUS") 
    list_edit_area(
        config.userconfigdict["NORMAL"], 
        [
            config.get_text("config_day"), 
            "",
            [
                config.get_text("config_location"),
                config.get_text("config_level"),
                config.get_text("config_times")
            ]
        ], 
        config.get_text("config_desc_list_edit"),
        has_switch=True
    )

    