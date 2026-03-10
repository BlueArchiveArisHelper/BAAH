from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_special(config):
    with ui.row():
        ui.link_target("SPECIAL_TASK")
        ui.label(config.get_text("task_special")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_times"))
    ui.switch(config.get_text("config_event_status")).bind_value(config.userconfigdict, "SPEICAL_EVENT_STATUS") 
    list_edit_area(
        config.userconfigdict["SPECIAL_HIGHTEST_LEVEL"], 
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
        has_switch=True,
        min_value_for_2nd_dim=-1
    )
            