from nicegui import ui
from gui.components.edit_team_strength import edit_the_team_strength_of_this_config
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName

def set_explore(config, real_taskname_to_show_taskname, logArea):
    ui.label(config.get_text("desc_team_strength"))
    # --------推图队伍设置-----------
    # 是否自动配队
    ui.checkbox(config.get_text("config_auto_team")).bind_value(config.userconfigdict, "EXPLORE_AUTO_TEAM")

    # 是否自动根据队伍属性选择队伍，与自动配队互斥
    ui.checkbox(config.get_text("config_rainbow_teams_desc")).bind_value(config.userconfigdict, "EXPLORE_RAINBOW_TEAMS").bind_visibility_from(config.userconfigdict, "EXPLORE_AUTO_TEAM", lambda x: not x)

    # 如果没有自动配队或者自动选择队伍属性，则手动选择队伍，提示无法通过GUI运行
    with ui.row().bind_visibility_from(config.userconfigdict, "EXPLORE_AUTO_TEAM", lambda x: not x):
        ui.label(config.get_text("desc_cli_since_manual")).style("color: red; font-size: x-large;").bind_visibility_from(config.userconfigdict, "EXPLORE_RAINBOW_TEAMS", lambda x: not x)

    with ui.card().bind_visibility_from(config.userconfigdict, "EXPLORE_AUTO_TEAM", lambda x: not x):
        edit_the_team_strength_of_this_config(config, "TEAM_SET_STRENGTH")

    # -----------normal explore--------------
    ui.label(config.get_text("push_normal")).style('font-size: x-large')
    
    ui.label(config.get_text("config_explore_attention"))
    
    with ui.row():
        with ui.card():
            ui.checkbox(config.get_text("config_use_simple_explore")).bind_value(config.userconfigdict, "PUSH_NORMAL_USE_SIMPLE")
            ui.number(config.get_text("config_push_normal_desc"), min=4, precision=0, step=1).bind_value(config.userconfigdict, "PUSH_NORMAL_QUEST", forward=lambda x: int(x)).classes("baah-w-short")
            ui.number(config.get_text("config_level"), min=1, precision=0, step=1).bind_value(config.userconfigdict, "PUSH_NORMAL_QUEST_LEVEL", forward=lambda x:int(x)).classes("baah-w-short")
        show_fast_run_task_buttons([TaskName.PUSH_NORMAL], config, real_taskname_to_show_taskname, logArea, show_desc=False)
        
    # ----------hard explore-------------
    ui.label(config.get_text("push_hard")).style('font-size: x-large')
    
    ui.label(config.get_text("config_explore_attention"))
    
    with ui.row():
        with ui.card():
            ui.checkbox(config.get_text("config_use_simple_explore")).bind_value(config.userconfigdict, "PUSH_HARD_USE_SIMPLE")
            ui.number(config.get_text("config_push_hard_desc"), min=1, precision=0, step=1).bind_value(config.userconfigdict, "PUSH_HARD_QUEST", forward=lambda x: int(x)).classes("baah-w-short")
            ui.number(config.get_text("config_level"), min=1, precision=0, step=1).bind_value(config.userconfigdict, "PUSH_HARD_QUEST_LEVEL", forward=lambda x:int(x)).classes("baah-w-short")
        show_fast_run_task_buttons([TaskName.PUSH_HARD], config, real_taskname_to_show_taskname, logArea, show_desc=False)
        
    