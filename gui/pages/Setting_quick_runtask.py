from nicegui import ui
from gui.components.fast_run_task_buttons import show_fast_run_task_buttons, TaskName

from gui.components.list_edit_area import list_edit_area

def set_quick_runtask(config, real_taskname_to_show_taskname, logArea):
    
    # 快速调用任务
    show_fast_run_task_buttons([
        TaskName.MOMOTALK, 
        [TaskName.MAIN_STORY, TaskName.SHORT_STORY, TaskName.SIDE_STORY],
        TaskName.SOLVE_CHALLENGE, 
        [TaskName.PUSH_NORMAL, TaskName.PUSH_HARD],
        TaskName.EVENTRECAP
    ], config, real_taskname_to_show_taskname, logArea)