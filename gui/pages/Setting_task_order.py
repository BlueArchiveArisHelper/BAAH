from nicegui import ui, run
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName
from modules.utils import return_now_activate_pipeline
from gui.components.modern_ui import confirm_delete, button_tip, info_tip
from gui.components.task_order_drag import enable_task_drag

def set_task_order(config, real_taskname_to_show_taskname, logArea):
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
        ui.label(config.get_text("config_pipelines_desc")).classes("text-subtitle2 text-grey-7")
        with ui.row().classes("items-center"):
            ui.toggle({ind:f"{config.get_text('config_pipeline')} {ind+1}" for ind in range(len(all_pipelines))}, value=activated_ind, on_change=lambda e:change_activated_pipeline(e)).props("no-caps")
            with ui.button(icon="add", on_click=add_one_pipeline).props("flat round dense"):
                button_tip(config, "tip_add_pipeline")
            if len(all_pipelines) > 1:
                with ui.button(icon="delete", on_click=ask_del_pipeline, color="red").props("flat round dense"):
                    ui.tooltip(config.get_text("config_delete_now_activated_pipeline"))
        # 当前被激活的pipeline
        with ui.card().classes("w-full"):
            with ui.list().props("padding separator").classes("w-full") as task_list:
                enable_task_drag(task_list, move_task)
                for i in range(len(task_pipeline)):
                    with ui.item().classes("baah-task-order-item").props(f"data-task-index={i}"):
                        with ui.item_section().props("side").classes("pr-2"):
                            ui.icon("drag_indicator").classes("baah-task-drag-handle").props("draggable=true")
                        # 启用开关（左侧 side section，不参与 flex 分配；pr-2 覆盖 Quasar side 默认 16px 间距，与行内 gap 统一为 8px）
                        with ui.item_section().props("side no-wrap").classes("pr-2"):
                            ui.checkbox(value=task_onoff[i], on_change=lambda v,i=i: task_onoff.__setitem__(i, v.value))
                        # 主内容：序号 + 任务下拉 + 添加/删除按钮（一行左→右排列，下拉撑开使按钮靠右）
                        with ui.item_section().props("no-wrap").classes("flex-1"):
                            with ui.row().classes("items-center w-full no-wrap gap-2"):
                                # 序号固定宽度+居中，保证各行下拉框左边缘对齐
                                ui.label(f'{config.get_text("config_task")} {i+1}:').classes("text-subtitle2 text-grey-7 text-no-wrap w-16 text-center shrink-0")
                                ui.select(real_taskname_to_show_taskname,
                                          value=task_pipeline[i],
                                          on_change=lambda v,i=i: task_pipeline.__setitem__(i, v.value),
                                          with_input=True
                                          ).props("dense outlined").classes("baah-w-long")
                                with ui.button(icon="add", on_click=lambda i=i+1: add_task(i)).props("flat round dense"):
                                    button_tip(config, "tip_add_task")
                                with ui.button(icon="delete", on_click=lambda i=i: del_task(i), color="red").props("flat round dense"):
                                    button_tip(config, "tip_remove_task")
                                with ui.button(icon="arrow_upward", on_click=lambda i=i: move_task(i, i - 1)).props("flat round dense" + (" disable" if i == 0 else "")):
                                    button_tip(config, "tip_move_up")
                                with ui.button(icon="arrow_downward", on_click=lambda i=i: move_task(i, i + 1)).props("flat round dense" + (" disable" if i == len(task_pipeline) - 1 else "")):
                                    button_tip(config, "tip_move_down")
            if len(task_pipeline) == 0:
                with ui.row().classes("w-full justify-center"):
                    ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda: add_task(0)).props("outline no-caps")

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

    def move_task(source, target):
        # 任务与启用状态一起移动，拖放和上下按钮共用相同的配置更新逻辑。
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if source == target or not (0 <= source < len(task_pipeline) and 0 <= target < len(task_pipeline)):
            return
        task_pipeline.insert(target, task_pipeline.pop(source))
        task_onoff.insert(target, task_onoff.pop(source))
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

    def ask_del_pipeline():
        # An empty pipeline loses nothing, so it goes without asking
        task_pipeline, _, _, activated_ind = return_now_activate_pipeline(config)
        if not task_pipeline:
            return del_one_pipeline()
        pipeline_str = f"{config.get_text('config_pipeline')} {activated_ind+1}"
        return confirm_delete(config, del_one_pipeline, "confirm_delete_pipeline", "confirm_delete_pipeline_tasks", pipeline=pipeline_str, tasks=len(task_pipeline))

    def change_activated_pipeline(e):
        # 切换要被激活的pipeline
        i = e.value
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if i >= len(all_pipelines):
            print(f"Target pipeline index {i} out of range {len(all_pipelines)}")
        config.userconfigdict["TASK_ORDER_GROUP"]["ACTIVATE_IND"] = i
        task_order.refresh()
    
    
    # pre-run command
    with info_tip(config, "tip_pre_command"):
        ui.input(config.get_text("config_pre_command"), placeholder='start cmd /c "BAAH.exe config1.json"').bind_value(config.userconfigdict, 'PRE_COMMAND').classes("baah-w-long")

    task_order()

    # post-run command
    with info_tip(config, "tip_post_command"):
        ui.input(config.get_text("config_post_command"), placeholder='start cmd /c "BAAH.exe config2.json"').bind_value(config.userconfigdict, 'POST_COMMAND').classes("baah-w-long")
    
    # with ui.row():
    #     ui.link_target("NEXT_CONFIG")
    #     ui.label(config.get_text("setting_next_config")).style('font-size: x-large')
    
    # ui.label(config.get_text("config_desc_next_config")).style('color: red')
        
    # ui.input(config.get_text("config_next_config")).bind_value(config.userconfigdict, 'NEXT_CONFIG',forward=lambda v: v.replace("\\", "/")).style('width: 400px')

    
    # 脚本运行报错自动重启脚本
    with ui.row():
        ui.number(config.get_text("desc_rerun_when_script_error"), min=0, max=10, precision=0, step=1).bind_value(config.userconfigdict, "RETRY_WHEN_ERROR", forward= lambda x: int(x)).classes("baah-w-short")
        ui.checkbox(config.get_text("desc_rerun_start_from_lastpoint")).bind_value(config.userconfigdict, "RETRY_WHEN_ERROR_FROM_LAST_TASK").bind_visibility_from(config.userconfigdict, "RETRY_WHEN_ERROR", backward=lambda x:x>0)


