from nicegui import ui, run
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName
from modules.utils import return_now_activate_pipeline

def set_task_order(config, real_taskname_to_show_taskname, logArea):
    with ui.row():
        ui.link_target("TASK_ORDER")
        ui.label(config.get_text("setting_task_order")).style('font-size: x-large')
    
    
    def select_clear_all_and_refresh_task_order(type="select"):
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if type == "select":
            for i in range(0, len(task_onoff)):
                task_onoff[i] = True
        else:
            for i in range(0, len(task_onoff)):
                task_onoff[i] = False
        task_order.refresh()
    
    with ui.row():
        ui.button(config.get_text("button_select_all"), on_click=lambda: select_clear_all_and_refresh_task_order("select"))
        ui.button(config.get_text("button_select_none"), on_click=lambda: select_clear_all_and_refresh_task_order("unselect"))
    
    @ui.refreshable
    def task_order():
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        # pipelines页签管理
        ui.label(config.get_text("config_pipelines_desc"))
        with ui.row():
            ui.toggle({ind:f"{config.get_text('config_pipeline')} {ind+1}" for ind in range(len(all_pipelines))}, value=activated_ind, on_change=lambda e:change_activated_pipeline(e))
            ui.button("+", on_click=add_one_pipeline)
            if len(all_pipelines) > 1:
                ui.button(config.get_text("config_delete_now_activated_pipeline"), on_click=del_one_pipeline, color="red")
        # 当前被激活的pipeline
        with ui.card():
            with ui.row():
                # 第一行添加上添加按钮
                ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda: add_task(0))
            for i in range(len(task_pipeline)):
                with ui.row():
                    ui.label(f'{config.get_text("config_task")} {i+1}:')
                    atask = ui.select(real_taskname_to_show_taskname,
                                    value=task_pipeline[i],
                                    on_change=lambda v,i=i: task_pipeline.__setitem__(i, v.value))
                    acheck = ui.checkbox(config.get_text("button_enable"), value=task_onoff[i], on_change=lambda v,i=i: task_onoff.__setitem__(i, v.value))
                    ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda i=i+1: add_task(i))
                    ui.button(f'{config.get_text("button_delete")} {config.get_text("config_task")}', on_click=lambda i=i: del_task(i), color="red")

    def add_task(i):
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        task_pipeline.insert(i, TaskName.MAIL)
        task_onoff.insert(i, True)
        task_order.refresh()
    
    def del_task(i):
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if len(task_pipeline) == 0:
            # 空列表的话不删除
            return
        task_pipeline.pop(i)
        task_onoff.pop(i)
        task_order.refresh()

    def add_one_pipeline():
        # 添加一个新的 pipeline，默认复制当前激活的pipeline
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if len(all_pipelines) == 0:
            all_pipelines.append({"TASK_PIPELINE":[], "TASK_ONOFF":[]})
            config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"] = 0
        else:
            now_pipeline = [each for each in task_pipeline]
            now_onoff = [each for each in task_onoff]
            all_pipelines.append({"TASK_PIPELINE":now_pipeline, "TASK_ONOFF":now_onoff})
            config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"] = len(all_pipelines)-1 # 这里的all_pipelines长度是添加了新的后的
        task_order.refresh()

    def del_one_pipeline():
        # 删除当前激活的这个pipeline
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if len(all_pipelines) > 1 and activated_ind < len(all_pipelines):
            # 确保删完至少还有一个pipeline
            all_pipelines.pop(activated_ind)
            config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"] = 0
        task_order.refresh()

    def change_activated_pipeline(e):
        # 切换要被激活的pipeline
        i = e.value
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if i >= len(all_pipelines):
            print(f"Target pipeline index {i} out of range {len(all_pipelines)}")
        config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"] = i
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


