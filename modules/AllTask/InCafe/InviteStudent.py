from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config


class InviteStudent(Task):
    """
    stuind 从0开始，邀请的学生的下标
    """

    def __init__(self, stuind, name="InviteStudent") -> None:
        super().__init__(name)
        self.stuind = stuind

    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_CAFE)

    def on_run(self) -> None:
        # 打开邀请界面
        open_momo = self.run_until(
            lambda: click((844, 652)),
            lambda: match(popup_pic(PopupName.POPUP_MOMOTALK)),
            times=3
        )
        if not open_momo:
            logging.warn({"zh_CN": "咖啡馆邀请界面打开失败, 跳出邀请任务",
                          "en_US": "Failed to open the cafe invite interface, jump out of the invitation task"})
            click(Page.MAGICPOINT)
            click(Page.MAGICPOINT)
            return
        # 打开确认弹窗
        # 默认邀请第一个学生
        click_pos = (787, 225)
        # 如果邀请第二个学生
        if self.stuind == 1:
            click_pos = (785, 303)
        # 邀请
        self.run_until(
            lambda: click(click_pos),
            lambda: match(button_pic(ButtonName.BUTTON_CONFIRMB))
        )
        # 确认，直到看不见通知确认按钮
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
            lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB))
        )
        click(Page.MAGICPOINT)
        click(Page.MAGICPOINT)
        config.sessiondict["CAFE_HAD_INVITED"] = True

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_CAFE)