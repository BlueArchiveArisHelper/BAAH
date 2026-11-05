from nicegui import ui
from gui.components.list_edit_area import list_edit_area
from gui.components.modern_ui import info_tip

def set_exchange(config):
    # ui.label(config.get_text("config_desc_times"))
    with info_tip(config, "tip_campaign_only"):
        ui.switch(config.get_text("config_campaign_only")).bind_value(config.userconfigdict, "EXCHANGE_EVENT_STATUS")
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
        column_tips=["tip_column_scrimmage", "tip_column_stage", "tip_column_times"],
        min_value_for_2nd_dim=-1,
        empty_line_prompt_id="config_no_tasks_set_here"
    )