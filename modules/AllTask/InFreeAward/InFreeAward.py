
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class InFreeAward(Task):
    def __init__(self, name="InFreeAward") -> None:
        super().__init__(name)
        self.COLOR_RED_POINT = [[10, 58, 247], [15, 65, 255]]
     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
     
    def on_run(self) -> None:
        # 打开商店页面
        logging.info(istr({
            CN: "尝试打开商店页面",
            EN: "Try open the shop page",
        }))
        open_shop = self.run_until(
            lambda: click([968, 38]),
            lambda: self.has_popup(),
            times = 3,
            sleeptime = 4
        )
        if not open_shop or not match_pixel([1030, 153], self.COLOR_RED_POINT, printit=True):
            logging.error(istr({
                CN: "无弹窗或无商店免费奖励红点，结束任务",
                EN: "No popup or no free award red point in shop, end task",
            }))
            return
        logging.info(istr({
            CN: "点击组合包领取页面",
            EN: "Click the bundle award page",
        }))
        see_free_collect = self.run_until(
            lambda: click( [900, 181]),
            lambda: match(button_pic(ButtonName.BUTTON_FREE_SHOP_BUY)),
            times = 3
        )
        if not see_free_collect:
            logging.error(istr({
                CN: "无免费奖励购买按钮，结束任务",
                EN: "No free award buy button, end task",
            }))
            return
        # 点击领取
        collect_free = self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_FREE_SHOP_BUY)),
            lambda: not match(button_pic(ButtonName.BUTTON_FREE_SHOP_BUY)),
            times = 2
        )
        if not collect_free:
            logging.error(istr({
                CN: "免费奖励领取失败(无免费按钮)",
                EN: "Free award collection failed (no free button)",
            }))
            return
        sleep(1)
        confirm_collect = self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY)),
            lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMY)),
            times = 1
        )
        if confirm_collect:
            logging.info(istr({
                CN: "免费奖励领取成功",
                EN: "Free award collection succeeded",
            }))
        else:
            logging.warning(istr({
                CN: "免费奖励领取失败(无确认按钮)",
                EN: "Free award collection failed (no confirm button)",
            }))

            
     
    def post_condition(self) -> bool:
        self.clear_popup()
        return self.back_to_home()