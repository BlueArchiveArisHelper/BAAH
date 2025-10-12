
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
from modules.AllTask.SubTask.ExecCode import ExecCode

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class UserTask(Task):
    """
    执行用户自定义任务，当自定义任务执行失败时，尝试返回游戏主页
    """
    def __init__(self, name="UserTask") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return True
    
     
    def on_run(self) -> None:
        content = config.userconfigdict["USER_DEF_TASKS"]
        runCode = ExecCode(content)
        runCode.run()
        if runCode.status == Task.STATUS_SUCCESS:
            logging.info(istr({
                CN: "自定义任务执行成功",
                EN: "Defined task success",
            }))
        elif runCode.status == Task.STATUS_ERROR:
            logging.error(istr({
                CN: "自定义任务执行错误，尝试返回游戏主页",
                EN: "Defined task error, try to return to the game homepage",
            }))
            self.back_to_home()

     
    def post_condition(self) -> bool:
        return True