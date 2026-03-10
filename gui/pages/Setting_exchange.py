from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_exchange(config):
    with ui.row():
        ui.link_target("EXCHANGE")
        ui.label(config.get_text("task_exchange")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_times"))
    ui.switch(config.get_text("config_event_status")).bind_value(config.userconfigdict, "EXCHANGE_EVENT_STATUS") 
    list_edit_area(
        config.userconfigdict["EXCHANGE_HIGHEST_LEVEL"], 
        [
            config.get_text("config_day"), 
            "",
            [
                config.get_text("config_academy"),
                config.get_text("config_level"),
                config.get_text("config_times")
            ]
        ], 
        config.get_text("config_desc_list_edit"),
        has_switch=True,
        min_value_for_2nd_dim=-1
    )