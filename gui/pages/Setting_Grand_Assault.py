from nicegui import ui
from gui.components.cut_screenshot import cut_screenshot, screencut_button
from gui.components.modern_ui import info_tip
from gui.pages.Setting_Assault import ASSAULT_TIERS

def set_grand_assault(config):

    # 分为左中右三个填写框
    # The tip covers all three areas, so its icon goes after the last one
    with info_tip(config, "tip_grand_assault_fight"):
        with ui.row():
            ui.select(ASSAULT_TIERS, label=config.get_text("desc_grand_assault_left_level")).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_LEFT_LEVEL").classes("baah-w-short")
            ui.select(ASSAULT_TIERS, label=config.get_text("desc_grand_assault_middle_level")).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_MIDDLE_LEVEL").classes("baah-w-short")
            ui.select(ASSAULT_TIERS, label=config.get_text("desc_grand_assault_right_level")).bind_value(config.userconfigdict, "AUTO_GRAND_ASSAULT_RIGHT_LEVEL").classes("baah-w-short")

    with info_tip(config, "tip_grand_assault_no_fight"):
        ui.checkbox(config.get_text("desc_grand_assault_no_fight")).bind_value(config.userconfigdict, "GRAND_ASSAULT_NO_FIGHT")
    with info_tip(config, "tip_grand_assault_no_team"):
        ui.checkbox(config.get_text("error_if_grand_assault_no_team")).bind_value(config.userconfigdict, "GRAND_ASSAULT_NO_TEAM_EXCEPT")