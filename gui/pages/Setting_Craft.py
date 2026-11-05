from nicegui import ui
from gui.components.modern_ui import info_tip

def set_craft(config):
    ui.label(config.get_text("config_craft_desc"))
    
    ui.number(config.get_text("config_craft_max_times"),
                step=1,
                precision=0,
                min=1,
                max=3
                ).bind_value(config.userconfigdict, 'CRAFT_TIMES', forward=lambda v: int(v), backward=lambda v:int(v)).classes("baah-w-short")
    
    with info_tip(config, "tip_use_quick_craft"):
        ui.checkbox(config.get_text("config_use_quick_craft")).bind_value(config.userconfigdict, 'CRAFT_USE_QUICK')