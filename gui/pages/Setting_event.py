from nicegui import ui
from gui.components.list_edit_area import list_edit_area
from gui.components.cut_screenshot import screencut_button

def set_event(config):
    with ui.row():
        ui.link_target("ACTIVITY")
        ui.label(config.get_text("task_event")).style('font-size: x-large')

    # 尝试进入活动的次数
    with ui.row().style("width: 100%; align-items: flex-start"):
        ui.label(config.get_text("config_try_enter_event_number"))
        ui.number(config.get_text("config_try_enter_event_number"), min=1, precision=0, step=1).bind_value(config.userconfigdict, "TRY_ENTER_EVENT_AFTER_FAIL_NUMBER", forward=lambda x:int(x))

    # 自动配队伍
    ui.checkbox(config.get_text("config_auto_team")).bind_value(config.userconfigdict, "ACTIVITY_AUTO_TEAM")
    
    ui.checkbox(config.get_text("config_auto_event_story")).bind_value(config.userconfigdict, "AUTO_EVENT_STORY_PUSH")
    
    with ui.row():
        ui.checkbox(config.get_text("config_auto_event_push")).bind_value(config.userconfigdict, "AUTO_PUSH_EVENT_QUEST")
        ui.checkbox(config.get_text("raise_error_if_can_not_push_event_level")).bind_value(config.userconfigdict, "RAISE_ERROR_IF_CANNOT_PUSH_EVENT_QUEST").bind_visibility_from(config.userconfigdict, "AUTO_PUSH_EVENT_QUEST")
    
    with ui.row().style("width: 100%; align-items: flex-start"):
        with ui.column().style("flex: 1 1 0; min-width: 0"):
            # 抽奖相关配置
            ui.label(config.get_text("config_event_roll_enter_desc"))
            screencut_button(config, config.userconfigdict, "EVENT_ENTER_ROLL_PAGE_BUTTON", save_folder_path=config.USER_STORAGE_FOLDER)
            ui.number(config.get_text("config_event_roll_times"),
                    min=0,precision=0,step=1).bind_value(config.userconfigdict, "EVENT_ROLL_TARGET_COUNT", forward=lambda x:int(x)).bind_visibility_from(config.userconfigdict, "EVENT_ENTER_ROLL_PAGE_BUTTON")
        with ui.column().style("flex: 1 1 0; min-width: 0"):
            # 赠品交换相关配置
            ui.label(config.get_text("config_event_exchange_enter_desc"))
            screencut_button(config, config.userconfigdict, "EVENT_ENTER_EXCHANGE_PAGE_BUTTON", save_folder_path=config.USER_STORAGE_FOLDER)

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
