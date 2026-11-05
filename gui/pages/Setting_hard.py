from nicegui import ui
from gui.components.list_edit_area import list_edit_area
from gui.components.modern_ui import all_configs_tag, info_tip

def set_hard(config, shared_softwareconfig):
    # ui.label(config.get_text("config_desc_times"))
    with info_tip(config, "tip_campaign_only_hard"):
        ui.switch(config.get_text("config_campaign_only")).bind_value(config.userconfigdict, "HARD_QUEST_EVENT_STATUS")
    
    show_note = {"val": False}
    show_note_label = config.get_text("show_note")
    with ui.row():
        ui.switch(show_note_label).bind_value(show_note, "val")
        all_configs_tag(config)
    ui.textarea().bind_value(shared_softwareconfig.softwareconfigdict["NOTE"], "HARD_NOTE").style("width: 70%").bind_visibility_from(show_note, "val")
    
    list_edit_area(
        config.userconfigdict["HARD"], 
        [
            config.get_text("config_day"), 
            "",
            [
                config.get_text("config_area"),
                config.get_text("config_level"),
                config.get_text("config_times")
            ]
        ], 
        config.get_text("config_desc_list_edit"),
        has_switch=True,
        column_tips=["tip_column_area", "tip_column_area_stage", "tip_column_times"],
        empty_line_prompt_id="config_no_tasks_set_here"
    )
