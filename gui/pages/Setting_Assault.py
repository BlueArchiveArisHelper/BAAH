from nicegui import ui
from gui.components.cut_screenshot import cut_screenshot, screencut_button
from gui.components.modern_ui import info_tip

# Difficulty names as the game shows them. Grand Assault stops at Torment, Total Assault adds Lunatic.
ASSAULT_TIERS = {1: "Normal", 2: "Hard", 3: "Very Hard", 4: "Hardcore", 5: "Extreme", 6: "Insane", 7: "Torment"}

def set_assault(config):
    # The tooltip below replaces this sentence. zh/jp have no tooltip yet, so they keep it.
    if not config.has_text("tip_assault_locked"):
        ui.label(config.get_text("desc_assault"))

    # zh/jp have no label yet, so they show the select without one
    target_label = config.get_text("config_assault_target_level")
    with info_tip(config, "tip_assault_locked"):
        ui.select({**ASSAULT_TIERS, 8: "Lunatic"}, label=target_label).bind_value(config.userconfigdict, "AUTO_ASSAULT_LEVEL").classes("baah-w-long")

    with info_tip(config, "tip_assault_no_team"):
        ui.checkbox(config.get_text("error_if_assault_no_team")).bind_value(config.userconfigdict, "ASSAULT_NO_TEAM_EXCEPT")

    # 是否自动配队
    # ui.checkbox(config.get_text("config_auto_team")).bind_value(config.userconfigdict, "IS_AUTO_ASSAULT_AUTO_TEAM")
    
    # 是否助战
    with info_tip(config, "tip_assault_helper"):
        ui.checkbox(config.get_text("config_need_assault_helper")).bind_value(config.userconfigdict, "IS_AUTO_ASSAULT_STUDENT_HELP")
    with ui.column().bind_visibility_from(config.userconfigdict, "IS_AUTO_ASSAULT_STUDENT_HELP"):
        # 助战是否后排
        ui.checkbox(config.get_text("config_assault_helper_is_support")).bind_value(config.userconfigdict, "AUTO_ASSAULT_HELP_STUDENT_IS_SUPPORT")
        
        screencut_button(inconfig=config, resultdict=config.userconfigdict, resultkey="AUTO_ASSAULT_HELP_STUDENT", input_text=config.get_text("config_assault_helper_student"), button_text=config.get_text("config_assault_helper_student"), save_folder_path=config.USER_STORAGE_FOLDER)