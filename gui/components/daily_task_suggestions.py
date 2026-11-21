from dataclasses import dataclass
from pathlib import Path

from nicegui import ui

from modules.AllTask.myAllTask import TaskName


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


def analyze_daily_tasks(task_pipeline: list[str]):
    """分析指定流程并返回建议卡片的绘制回调。"""
    result = check_daily_tasks(task_pipeline)

    def draw(config, real_taskname_to_show_taskname, panel_open: dict[str, bool]):
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
                value=panel_open.get(key, key != "optional"),
                on_value_change=lambda event: panel_open.__setitem__(key, event.value),
            ).classes("baah-description baah-expansion-compact").props(f"header-class={header_color}"):
                suggestion_items(items)
                if hint:
                    ui.label(hint).classes("baah-muted text-sm")

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

        with ui.card().classes("baah-aside-card") as card:
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

        return card

    return draw
