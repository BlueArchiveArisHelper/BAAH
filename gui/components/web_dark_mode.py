from nicegui import ui

async def apply_dark_mode(gui_shared_config):
    """根据配置应用暗色模式"""
    value = gui_shared_config.softwareconfigdict["DARK_MODE"]
    dark = ui.dark_mode()
    if value == "light":
        dark.disable()
    elif value == "dark":
        dark.enable()
    else: # system
        is_dark = await ui.run_javascript('window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches')
        if is_dark:
            dark.enable()
        else:
            dark.disable()

async def change_dark_mode(value, gui_shared_config):
    """更改暗色模式设置并应用"""
    gui_shared_config.softwareconfigdict["DARK_MODE"] = value
    gui_shared_config.save_software_config()
    await apply_dark_mode(gui_shared_config)