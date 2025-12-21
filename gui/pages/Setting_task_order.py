from nicegui import ui, run
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName

def set_task_order(config, real_taskname_to_show_taskname, logArea):
    with ui.row():
        ui.link_target("TASK_ORDER")
        ui.label(config.get_text("setting_task_order")).style('font-size: x-large')
    
    
    def select_clear_all_and_refresh_task_order(type="select"):
        if type == "select":
            for i in range(0, len(config.userconfigdict["TASK_ACTIVATE"])):
                config.userconfigdict["TASK_ACTIVATE"][i] = True
        else:
            for i in range(0, len(config.userconfigdict["TASK_ACTIVATE"])):
                config.userconfigdict["TASK_ACTIVATE"][i] = False
        task_order.refresh()
    
    with ui.row():
        ui.button(config.get_text("button_select_all"), on_click=lambda: select_clear_all_and_refresh_task_order("select"))
        ui.button(config.get_text("button_select_none"), on_click=lambda: select_clear_all_and_refresh_task_order("unselect"))
    
    @ui.refreshable
    def task_order():
        with ui.row():
            # 第一行添加上添加按钮
            ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda: add_task(0))
        for i in range(len(config.userconfigdict["TASK_ORDER"])):
            with ui.row():
                ui.label(f'{config.get_text("config_task")} {i+1}:')
                atask = ui.select(real_taskname_to_show_taskname,
                                  value=config.userconfigdict["TASK_ORDER"][i],
                                  on_change=lambda v,i=i: config.userconfigdict["TASK_ORDER"].__setitem__(i, v.value))
                acheck = ui.checkbox(config.get_text("button_enable"), value=config.userconfigdict["TASK_ACTIVATE"][i], on_change=lambda v,i=i: config.userconfigdict["TASK_ACTIVATE"].__setitem__(i, v.value))
                ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda i=i+1: add_task(i))
                ui.button(f'{config.get_text("button_delete")} {config.get_text("config_task")}', on_click=lambda i=i: del_task(i), color="red")

    def add_task(i):
        config.userconfigdict["TASK_ORDER"].insert(i, TaskName.MAIL)
        config.userconfigdict["TASK_ACTIVATE"].insert(i, True)
        task_order.refresh()
    
    def del_task(i):
        if len(config.userconfigdict["TASK_ORDER"]) == 0:
            # 空列表的话不删除
            return
        config.userconfigdict["TASK_ORDER"].pop(i)
        config.userconfigdict["TASK_ACTIVATE"].pop(i)
        task_order.refresh()
    
    
    # pre-run command
    with ui.row():
        ui.input(config.get_text("config_pre_command"), placeholder='start cmd /c "BAAH.exe config1.json"').bind_value(config.userconfigdict, 'PRE_COMMAND').style('width: 300px')
    
    task_order()
    
    # post-run command
    with ui.row():
        ui.input(config.get_text("config_post_command"), placeholder='start cmd /c "BAAH.exe config2.json"').bind_value(config.userconfigdict, 'POST_COMMAND').style('width: 300px')
    
    # with ui.row():
    #     ui.link_target("NEXT_CONFIG")
    #     ui.label(config.get_text("setting_next_config")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_next_config")).style('color: red')
        
    # ui.input(config.get_text("config_next_config")).bind_value(config.userconfigdict, 'NEXT_CONFIG',forward=lambda v: v.replace("\\", "/")).style('width: 400px')

    
    # 脚本运行报错自动重启脚本
    with ui.row():
        ui.number(config.get_text("desc_rerun_when_script_error"), min=0, max=10, precision=0, step=1).bind_value(config.userconfigdict, "RETRY_WHEN_ERROR", forward= lambda x: int(x)).style("width: 400px")
        ui.checkbox(config.get_text("desc_rerun_start_from_lastpoint")).bind_value(config.userconfigdict, "RETRY_WHEN_ERROR_FROM_LAST_TASK").bind_visibility_from(config.userconfigdict, "RETRY_WHEN_ERROR", backward=lambda x:x>0)


    # 快速调用任务
    show_fast_run_task_buttons([
        TaskName.MOMOTALK, 
        [TaskName.MAIN_STORY, TaskName.SHORT_STORY, TaskName.SIDE_STORY],
        TaskName.SOLVE_CHALLENGE, 
        [TaskName.PUSH_NORMAL, TaskName.PUSH_HARD],
        TaskName.EVENTRECAP
    ], config, real_taskname_to_show_taskname, logArea)

