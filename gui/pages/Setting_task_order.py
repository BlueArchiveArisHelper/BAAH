from dataclasses import dataclass
from pathlib import Path

from nicegui import app, ui

from gui.components.modern_ui import button_tip, confirm_delete, info_tip
from modules.AllTask.myAllTask import TaskName
from modules.utils import return_now_activate_pipeline


RECOMMENDED_DAILY_TASKS = (
    TaskName.CAFE,
    TaskName.TIMETABLE,
    TaskName.CLUB,
    TaskName.SCHOOL_EXCHANGE_MEETING,
    TaskName.BOUNTY,
    (TaskName.HARD, TaskName.ONE_CLICK_RAID),
    TaskName.TACTICAL_CHALLENGE,
    TaskName.MAIL,
    TaskName.DAILY,
)
OPTIONAL_DAILY_TASKS = (TaskName.MANUFACTURE, TaskName.STORE, TaskName.SPECIAL)
STAMINA_TASKS = (TaskName.ONE_CLICK_RAID, TaskName.NORMAL, TaskName.HARD, TaskName.EVENT)
DAILY_ARENA_TARGET = 5
DAILY_TASK_COVERED_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "Goods_Icon_Gem_4900_Preset_2.png"


@dataclass
class DailyTaskCheck:
    missing_recommended: list[tuple[str, ...]]
    missing_optional: list[str]
    arena_rounds: int
    late_timetable: bool
    pickups_without_stamina: list[str]


def check_daily_tasks(task_pipeline: list[str]) -> DailyTaskCheck:
    first_positions = {}
    last_stamina_position = -1
    for index, task in enumerate(task_pipeline):
        first_positions.setdefault(task, index)
        if task in STAMINA_TASKS:
            last_stamina_position = index

    recommended_alternatives = [(item,) if isinstance(item, str) else item for item in RECOMMENDED_DAILY_TASKS]
    daily_position = first_positions.get(TaskName.DAILY)
    timetable_position = first_positions.get(TaskName.TIMETABLE)
    return DailyTaskCheck(
        missing_recommended=[
            alternatives for alternatives in recommended_alternatives
            if not any(task in first_positions for task in alternatives)
        ],
        missing_optional=[task for task in OPTIONAL_DAILY_TASKS if task not in first_positions],
        arena_rounds=task_pipeline.count(TaskName.TACTICAL_CHALLENGE),
        late_timetable=(
            daily_position is not None
            and timetable_position is not None
            and daily_position < timetable_position
        ),
        pickups_without_stamina=[
            task for task in (TaskName.DAILY, TaskName.MAIL)
            if first_positions.get(task, -1) > last_stamina_position
        ],
    )


def set_task_order(config, real_taskname_to_show_taskname, logArea):
    preferences = app.storage.user
    preference_key = "show_daily_task_suggestions"
    # 各建议面板的展开状态，刷新后保持；潜在问题与建议默认展开。
    panel_open = {"warning": True, "recommended": True, "optional": False}

    def missing_task_suggestions(alternatives_list):
        add_task_text = config.get_text("daily_task_check_add_task")
        add_either_text = config.get_text("daily_task_check_add_either_task")
        suggestions = []
        for alternatives in alternatives_list:
            names = [real_taskname_to_show_taskname[task] for task in alternatives]
            suggestions.append(
                add_task_text.format(task=names[0]) if len(names) == 1
                else add_either_text.format(task=names[0], other=names[1])
            )
        return suggestions

    def suggestion_items(items):
        with ui.element("ul").classes("m-0 list-disc pl-5"):
            for item in items:
                with ui.element("li"):
                    ui.label(item)

    def suggestion_group(key, title, icon, items, *, hint=None):
        header_color = {"warning": "text-warning", "recommended": "text-primary"}.get(key, "text-grey-7")
        with ui.expansion(
            config.get_text(title),
            icon=icon,
            value=panel_open[key],
            on_value_change=lambda event: panel_open.__setitem__(key, event.value),
        ).classes("baah-description baah-expansion-compact").props(f"header-class={header_color}"):
            suggestion_items(items)
            if hint:
                ui.label(hint).classes("baah-muted text-sm")

    def toggle_daily_task_suggestions(event):
        preferences[preference_key] = event.value
        daily_task_suggestions.refresh()

    def update_task(task_pipeline, index, value):
        task_pipeline[index] = value
        daily_task_suggestions.refresh()

    @ui.refreshable
    def daily_task_suggestions():
        if not preferences.get(preference_key, True):
            return

        task_pipeline, _, _, _ = return_now_activate_pipeline(config)
        result = check_daily_tasks(task_pipeline)
        order_notes = []
        if result.late_timetable:
            order_notes.append(config.get_text("daily_task_check_timetable").format(
                timetable=real_taskname_to_show_taskname[TaskName.TIMETABLE],
                daily=real_taskname_to_show_taskname[TaskName.DAILY],
            ))

        stamina_hint = None
        if result.pickups_without_stamina:
            stamina_template = config.get_text("daily_task_check_stamina")
            for pickup in result.pickups_without_stamina:
                order_notes.append(stamina_template.format(pickup=real_taskname_to_show_taskname[pickup]))
            stamina_names = config.get_text("daily_task_check_separator").join(
                f"「{real_taskname_to_show_taskname[task]}」" for task in STAMINA_TASKS
            )
            stamina_hint = config.get_text("daily_task_check_stamina_options").format(tasks=stamina_names)

        optional_notes = missing_task_suggestions([(task,) for task in result.missing_optional])
        # 缺少竞技场时已有强烈建议，安排过场次后再提示补足。
        if 0 < result.arena_rounds < DAILY_ARENA_TARGET:
            optional_notes.append(config.get_text("daily_task_check_arena").format(
                arena=real_taskname_to_show_taskname[TaskName.TACTICAL_CHALLENGE],
                count=result.arena_rounds,
                target=DAILY_ARENA_TARGET,
            ))

        with ui.card().classes("baah-aside-card"):
            ui.label(config.get_text("daily_task_check_title")).classes("text-subtitle1")
            if order_notes:
                suggestion_group("warning", "daily_task_check_warning", "warning", order_notes, hint=stamina_hint)
            if result.missing_recommended:
                suggestion_group(
                    "recommended", "daily_task_check_recommended", "info_outline",
                    missing_task_suggestions(result.missing_recommended),
                )
            if not order_notes and not result.missing_recommended:
                with ui.column().classes("w-full items-center gap-1 py-2 text-center"):
                    ui.image(DAILY_TASK_COVERED_IMAGE).classes("w-36 max-w-full").props('fit=contain alt="" no-spinner')
                    ui.label(config.get_text("daily_task_check_covered")).classes("text-subtitle1 font-medium")
                    ui.label(config.get_text("daily_task_check_covered_detail")).classes("baah-muted text-sm")

            if optional_notes:
                suggestion_group("optional", "daily_task_check_optional", "lightbulb_outline", optional_notes)

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
            ui.switch(
                config.get_text("daily_task_check_switch"),
                value=preferences.get(preference_key, True),
                on_change=toggle_daily_task_suggestions,
            ).props("dense")

        # 任务列表和建议卡片按可用宽度换行；列表保持自身内容宽度。
        with ui.row().classes("w-full items-start"):
            with ui.card().classes("min-w-0 max-w-full"):
                with ui.list().props("padding").classes("max-w-full"):
                    for i in range(len(task_pipeline)):
                        with ui.item():
                            # 启用开关（左侧 side section，不参与 flex 分配；pr-2 覆盖 Quasar side 默认 16px 间距，与行内 gap 统一为 8px）
                            with ui.item_section().props("side no-wrap").classes("pr-2"):
                                ui.checkbox(value=task_onoff[i], on_change=lambda v, i=i: task_onoff.__setitem__(i, v.value))
                            # 主内容：序号 + 任务下拉 + 添加/删除按钮（一行左→右排列，下拉撑开使按钮靠右）
                            with ui.item_section().props("no-wrap").classes("min-w-0 flex-1"):
                                with ui.row().classes("items-center w-full no-wrap gap-2"):
                                    # 序号固定宽度+居中，保证各行下拉框左边缘对齐
                                    ui.label(f'{config.get_text("config_task")} {i+1}:').classes("text-subtitle2 text-grey-7 text-no-wrap w-16 text-center shrink-0")
                                    ui.select(real_taskname_to_show_taskname,
                                              value=task_pipeline[i],
                                              on_change=lambda v, i=i: update_task(task_pipeline, i, v.value),
                                              with_input=True
                                              ).props("dense outlined").classes("baah-w-long min-w-0")
                                    with ui.button(icon="add", on_click=lambda i=i+1: add_task(i)).props("flat round dense"):
                                        button_tip(config, "tip_add_task")
                                    with ui.button(icon="delete", on_click=lambda i=i: del_task(i), color="red").props("flat round dense"):
                                        button_tip(config, "tip_remove_task")
                                    with ui.button(icon="arrow_upward", on_click=lambda i=i: move_task_up(i)).props("flat round dense" + (" disable" if i == 0 else "")):
                                        button_tip(config, "tip_move_up")
                                    with ui.button(icon="arrow_downward", on_click=lambda i=i: move_task_down(i)).props("flat round dense" + (" disable" if i == len(task_pipeline) - 1 else "")):
                                        button_tip(config, "tip_move_down")
                        ui.separator()
                if len(task_pipeline) == 0:
                    with ui.row().classes("w-full justify-center"):
                        ui.button(f'{config.get_text("button_add")} {config.get_text("config_task")}', on_click=lambda: add_task(0)).props("outline no-caps")
            daily_task_suggestions()

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

    def move_task_up(i):
        # 将第i个任务上移一格
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if i <= 0:
            return
        task_pipeline[i - 1], task_pipeline[i] = task_pipeline[i], task_pipeline[i - 1]
        task_onoff[i - 1], task_onoff[i] = task_onoff[i], task_onoff[i - 1]
        task_order.refresh()

    def move_task_down(i):
        # 将第i个任务下移一格
        task_pipeline, task_onoff, all_pipelines, activated_ind = return_now_activate_pipeline(config)
        if i >= len(task_pipeline) - 1:
            return
        task_pipeline[i + 1], task_pipeline[i] = task_pipeline[i], task_pipeline[i + 1]
        task_onoff[i + 1], task_onoff[i] = task_onoff[i], task_onoff[i + 1]
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


