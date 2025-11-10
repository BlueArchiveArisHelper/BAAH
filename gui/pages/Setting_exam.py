from nicegui import ui
from gui.components.cut_screenshot import cut_screenshot, screencut_button

def set_exam(config):

    with ui.row():
        ui.link_target("EXAM")
        ui.label(config.get_text("task_exam")).style('font-size: x-large')

    # 设置考试关卡
    ui.number(config.get_text("config_level"),
              min=1, max=4, step=1, precision=0).bind_value(
                  config.userconfigdict, "EXAM_TARGET_LEVEL",
                  forward=lambda x: int(x)
                  ).style('width: 200px')
    # 设置考试的队伍数量
    ui.number(config.get_text("desc_exam_times"), 
              min=1, max=3, step=1, precision=0).bind_value(
                  config.userconfigdict, "EXAM_TEAM_COUNT",
                  forward=lambda x: int(x)
                  ).style('width: 200px')
    # 如果考试失败则尝试挑战上一关卡
    ui.checkbox(config.get_text("desc_exam_allow_fallback")).bind_value(config.userconfigdict, "EXAM_ALLOW_FALLBACK")

    # 使用助战学生
    ui.checkbox(config.get_text("config_need_exam_helper")).bind_value(config.userconfigdict, "IS_EXAM_STUDENT_HELP")
    with ui.column().bind_visibility_from(config.userconfigdict, "IS_EXAM_STUDENT_HELP"):
        # 助战是否后排
        ui.checkbox(config.get_text("config_exam_helper_is_support")).bind_value(config.userconfigdict, "EXAM_HELP_STUDENT_IS_SUPPORT")
        # 助战学生截图按钮
        screencut_button(inconfig=config, resultdict=config.userconfigdict, resultkey="EXAM_HELP_STUDENT", input_text=config.get_text("config_exam_helper_student"), button_text=config.get_text("config_exam_helper_student"))