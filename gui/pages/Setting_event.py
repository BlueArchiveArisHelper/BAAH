from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_event(config):
    with ui.row():
        ui.link_target("ACTIVITY")
        ui.label(config.get_text("task_event")).style('font-size: x-large')

    # 自动配队伍
    ui.checkbox(config.get_text("config_auto_team")).bind_value(config.userconfigdict, "ACTIVITY_AUTO_TEAM")
    
    ui.checkbox(config.get_text("config_auto_event_story")).bind_value(config.userconfigdict, "AUTO_EVENT_STORY_PUSH")
    
    with ui.row():
        ui.checkbox(config.get_text("config_auto_event_push")).bind_value(config.userconfigdict, "AUTO_PUSH_EVENT_QUEST")
        ui.checkbox(config.get_text("raise_error_if_can_not_push_event_level")).bind_value(config.userconfigdict, "RAISE_ERROR_IF_CANNOT_PUSH_EVENT_QUEST").bind_visibility_from(config.userconfigdict, "AUTO_PUSH_EVENT_QUEST")
    
    # ui.label(config.get_text("config_desc_times"))
    list_edit_area(
        config.userconfigdict["EVENT_QUEST_LEVEL"], 
        [
            config.get_text("config_day"), 
            "", 
            [
                config.get_text("config_level"), 
                config.get_text("config_times")
            ]
        ], 
        config.get_text("config_desc_list_edit"),
        has_switch=True
    )
