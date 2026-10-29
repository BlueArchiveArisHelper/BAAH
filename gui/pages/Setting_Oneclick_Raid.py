from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_oneclick_raid(config):
    # 一键扫荡
    ui.label(config.get_text("task_oneclick_raid")).style('font-size: x-large')
    ui.checkbox(config.get_text("config_event_status")).bind_value(config.userconfigdict, "DO_ONE_CLICK_RAID_ONLY_DURING_EVENT")
    with ui.row().bind_visibility_from(config.userconfigdict, "DO_ONE_CLICK_RAID_ONLY_DURING_EVENT"): 
        ui.switch(f'{config.get_text("config_event_status")} ({config.get_text("word_normal")})').bind_value(config.userconfigdict, "DO_ONE_CLICK_RAID_ONLY_DURING_NORMAL_TRIPLE") 
        ui.switch(f'{config.get_text("config_event_status")} ({config.get_text("word_hard")})').bind_value(config.userconfigdict, "DO_ONE_CLICK_RAID_ONLY_DURING_HARD_TRIPLE") 
    list_edit_area(
        config.userconfigdict["ONE_CLICK_RAID"],
        [
            config.get_text("config_day"), 
            "",
            [
                config.get_text("config_task"),
                config.get_text("config_times")
            ]
        ],
        config.get_text("desc_one_click_raid"),
        # 一键扫荡的使用前提统一展示为信息提醒框。
        has_switch=True,
        blockdesc_as_notice=True
    )