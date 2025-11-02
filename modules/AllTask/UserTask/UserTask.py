
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
from modules.AllTask.SubTask.ExecCode import ExecCode

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging
from define_actions import FlowActionGroup

class UserTask(Task):
    """
    执行用户自定义任务，当自定义任务执行失败时，尝试返回游戏主页
    """
    def __init__(self, name="UserTask") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return True
    
    def _do_exec_def_task(self):
        """使用exec执行python代码"""
        content = config.userconfigdict["USER_DEF_TASKS"]
        runCode = ExecCode(content)
        runCode.run()
        return runCode.status

    def _do_action_def_obj(self):
        """使用action obj执行对象化任务"""
        content = config.userconfigdict["OBJ_USER_DEFINE_TASK"]
        flowaction = FlowActionGroup().load_from_dict(content)
        success = flowaction.run_flow()
        return Task.STATUS_SUCCESS if success else Task.STATUS_ERROR

     
    def on_run(self) -> None:
        if not config.userconfigdict["USE_OBJ_USER_DEFINE_TASK"]:
            # 使用exec执行python代码
            status = self._do_exec_def_task()
        else:
            # 使用action obj
            status = self._do_action_def_obj()


        if status == Task.STATUS_SUCCESS:
            logging.info(istr({
                CN: "自定义任务执行成功",
                EN: "Defined task success",
            }))
        elif status == Task.STATUS_ERROR:
            logging.error(istr({
                CN: "自定义任务执行错误，尝试返回游戏主页",
                EN: "Defined task error, try to return to the game homepage",
            }))
            self.back_to_home()

     
    def post_condition(self) -> bool:
        return True