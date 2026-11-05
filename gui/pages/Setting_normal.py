from nicegui import ui
from gui.components.edit_team_strength import edit_the_team_strength_of_this_config
from gui.components.list_edit_area import list_edit_area
from gui.components.modern_ui import info_tip

def set_normal(config):
    # ui.label(config.get_text("config_desc_times"))
    with info_tip(config, "tip_campaign_only"):
        ui.switch(config.get_text("config_campaign_only")).bind_value(config.userconfigdict, "NORMAL_QUEST_EVENT_STATUS")
    list_edit_area(
        config.userconfigdict["NORMAL"], 
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

    