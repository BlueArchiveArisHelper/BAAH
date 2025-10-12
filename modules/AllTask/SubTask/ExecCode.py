
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class ExecCode(Task):
    """
    使用exec执行自定义代码
    """
    def __init__(self, content, name="ExecCode") -> None:
        super().__init__(name)
        self.content = content

     
    def pre_condition(self) -> bool:
        return True
    
     
    def on_run(self) -> None:
        if not self.content or len(self.content)==0:
            logging.warn(istr({
                CN: "自定义任务为空",
                EN: "Defined task is empty",
            }))
        try:
            exec(self.content)
            self.status = self.STATUS_SUCCESS
        except Exception as e:
            logging.error(istr({
                CN: "自定义任务执行错误",
                EN: "Defined task error",
            }))
            logging.error(e)
            self.status = self.STATUS_ERROR

     
    def post_condition(self) -> bool:
        return True