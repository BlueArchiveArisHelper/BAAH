
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging
from .InviteStudent import InviteStudent

class BuyTicket(Task):
    def __init__(self, name="BuyTicket") -> None:
        super().__init__(name)
        # 默认购买失败
        self.status = Task.STATUS_SKIP
     
    def pre_condition(self) -> bool:
        self.clear_popup()
        return match(page_pic(PageName.PAGE_CAFE))
    
     
    def on_run(self) -> None:
        super().on_run()
        # 购买票卷
        open_buy_popup = self.run_until(
            lambda: click([743, 656]),
            lambda: self.has_popup(),
            times = 3
        )
        if not open_buy_popup:
            logging.error(istr({
                CN: "咖啡馆购买票卷界面打开失败，跳出购买任务",
                EN: "Failed to open the cafe ticket purchase interface, jump out of purchase task"
            }))
            return
        else:
            logging.info(istr({
                CN: "成功打开咖啡馆购买票卷界面",
                EN: "Successfully opened the cafe ticket purchase interface"
            }))

        buy_ticket = self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY)),
            lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMY)),
            times = 3
        )
        if not buy_ticket:
            logging.error(istr({
                CN: "咖啡馆购买票卷失败",
                EN: "Failed to buy tickets at the cafe"
            }))
            return
        else:
            logging.info(istr({
                CN: "成功购买咖啡馆票卷",
                EN: "Successfully purchased cafe tickets"
            }))
        self.status = Task.STATUS_SUCCESS
        

     
    def post_condition(self) -> bool:
        self.clear_popup()
        return match(page_pic(PageName.PAGE_CAFE))