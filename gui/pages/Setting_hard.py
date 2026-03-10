from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_hard(config, shared_softwareconfig):
    with ui.row():
        ui.link_target("HARD")
        ui.label(config.get_text("task_hard")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_times"))
    ui.switch(config.get_text("config_event_status")).bind_value(config.userconfigdict, "HARD_QUEST_EVENT_STATUS") 
    
    show_note = {"val": False}
    ui.switch(config.get_text("button_show")+config.get_text("desc_note")).bind_value(show_note, "val")
    ui.textarea().bind_value(shared_softwareconfig.softwareconfigdict["NOTE"], "HARD_NOTE").style("width: 70%").bind_visibility_from(show_note, "val")
    
    list_edit_area(
        config.userconfigdict["HARD"], 
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
