from gui.components.manage_baah_in_gui import run_baah_task_and_bind_log
from nicegui import ui, run
from modules.AllTask.myAllTask import TaskName

def show_fast_run_task_buttons(task_confname_list, config, real_taskname_to_show_taskname, logArea, show_title=True, show_desc=False):
    """
    展示快速运行任务按钮
    """
    if show_title:
        ui.label(config.get_text("config_quick_call_task")).style('font-size: x-large')
    
    if show_desc:
        ui.label(config.get_text("config_desc_quick_call_task"))

    def gui_just_run_one_task(taskname):
        async def just_run_one_task():
            logArea.push(f"Task Running")
            config.save_user_config(config.nowuserconfigname)
            await run.io_bound(run_baah_task_and_bind_log, logArea, config.nowuserconfigname, taskname)
        ui.button(real_taskname_to_show_taskname[taskname], on_click=just_run_one_task)
    
    # show buttons
    for t_cn_line in task_confname_list:
        with ui.row():
            if isinstance(t_cn_line, str):
                # 字符串
                gui_just_run_one_task(t_cn_line)
            else:
                # 列表
                for t_cn in t_cn_line:
                    gui_just_run_one_task(t_cn)