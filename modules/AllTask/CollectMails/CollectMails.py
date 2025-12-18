 

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep

class CollectMails(Task):
    def __init__(self, name="CollectMails") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    
    def on_run(self) -> None:
        if not self.run_until(
            lambda: click((1143, 38)),
            lambda: Page.is_page(PageName.PAGE_MAILBOX)
        ):
            # 如果没到邮箱界面，返回主页
            return
        click(Page.MAGICPOINT)
        click(Page.MAGICPOINT)
        if not match(button_pic(ButtonName.BUTTON_ONE_COLLECT), threshold=0.95):
            # 简单适配下高画质收取邮箱
            click((1133, 673))
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_ONE_COLLECT)),
            lambda: not match(button_pic(ButtonName.BUTTON_ONE_COLLECT), threshold=0.95)
        )
        
        self.back_to_home()

     
    def post_condition(self) -> bool:
        return self.back_to_home()