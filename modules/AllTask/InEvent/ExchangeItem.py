
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging
from .EventHelper import from_inner_page_safe_back_to_event_page

class ExchangeItem(Task):
    def __init__(self, name="ExchangeItem") -> None:
        super().__init__(name)
        # 交换按钮（黄色）位置
        self.exchange_button_xy = [403, 676]
        # 点完按钮后蓝色确定按钮位置
        self.blue_confirm_xy = [622, 609]
        self.blue_confirm_color = [(235, 202, 100), (255, 242, 140)]
        # 右上角 立即更新奖池 按钮
        self.refresh_pool_xy = [1158, 114]
        # 奖池背景暗色（表示要刷新了）
        self.pool_bck_xy = [948, 166]
        self.pool_bck_color = [(30, 24, 15), (50, 44, 35)]
        

     
    def pre_condition(self) -> bool:
        return super().pre_condition()
    
     
    def on_run(self) -> None:
        """
        处理赠品交换页面，从活动主页面进入赠品交换页面，点击赠品交换按钮，然后返回活动主页面
        """
        self.clear_popup()
        exchange_page_button_pos = match(config.userconfigdict["EVENT_ENTER_EXCHANGE_PAGE_BUTTON"], returnpos=True)
        if not exchange_page_button_pos[0]:
            logging.info(istr({
                CN: f"未能识别赠品交换页面入口按钮 {exchange_page_button_pos}，跳过赠品交换。可能截取的图片已过时？",
                EN: f"Failed to recognize the entrance button of the exchange page {exchange_page_button_pos}, skip the exchange. Maybe the captured picture is outdated?"
            }))
            return

        # 点击赠品交换页面入口按钮，直到按钮消失
        enter_roll_page = self.run_until(
            lambda: click(config.userconfigdict["EVENT_ENTER_EXCHANGE_PAGE_BUTTON"], sleeptime=2),
            lambda: not match(config.userconfigdict["EVENT_ENTER_EXCHANGE_PAGE_BUTTON"])
        )
        # 判断是否进入赠品交换页面
        if not enter_roll_page:
            logging.warn(istr({
                CN: f"点击赠品交换页面入口按钮 {config.userconfigdict['EVENT_ENTER_EXCHANGE_PAGE_BUTTON']} 失败，未能进入赠品交换页面",
                EN: f"Click the entrance button of the exchange page {config.userconfigdict['EVENT_ENTER_EXCHANGE_PAGE_BUTTON']} failed, failed to enter the exchange page"
            }))
            return
        # 根据奖池背景明暗判断是不是要刷新奖池了
        sleep(1.5)
        screenshot()
        pool_is_dark = match_pixel(self.pool_bck_xy, self.pool_bck_color, printit=True)
        if pool_is_dark:
            success_click_refresh = self.run_until(
                lambda: click(self.refresh_pool_xy),
                lambda: self.has_popup(),
                times = 3
            )
            success_click_confirmb = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                lambda: not self.has_popup(),
                times = 3
            )
            logging.info(istr({
                CN: f"奖池背景较暗，刷新奖池。{success_click_refresh} {success_click_confirmb}",
                EN: f"Background of pool is dark, refresh.{success_click_refresh} {success_click_confirmb}"
            }))


        # 判断按钮是否是亮着的
        sleep(1.5)
        screenshot()
        yellow_button_is_on = match_pixel(self.exchange_button_xy, Page.COLOR_BUTTON_YELLOW, printit=True)
        if not yellow_button_is_on:
            logging.warn(istr({
                CN: f"赠品交换按钮未亮起，跳过赠品交换",
                EN: f"The exchange button is not lit, skip the exchange"
            }))
            return
        # 点击赠品交换按钮
        logging.info(istr({
            CN: f"点击交换按钮",
            EN: f"Click exchange button"
        }))
        success_click = self.run_until(
            lambda: click(self.exchange_button_xy),
            lambda: not match_pixel(self.exchange_button_xy, Page.COLOR_BUTTON_YELLOW, printit=True),
            times=3,
            sleeptime=1.5
        )
        # 会弹出一个全屏的物品结算页面，需要点击左下角蓝色确认按钮
        # 不管咋样先点一下
        click(self.blue_confirm_xy)
        success_confirm_blue = self.run_until(
            lambda: click(self.blue_confirm_xy),
            lambda: not match_pixel(self.blue_confirm_xy, self.blue_confirm_color, printit=True),
        )
        logging.info(istr({
            CN: f"点击交换按钮：{success_click}，点结算确认：{success_confirm_blue}",
            EN: f"click exchange: {success_click}, click confirm blue: {success_confirm_blue}"
        }))
        self.clear_popup()

     
    def post_condition(self) -> bool:
        return from_inner_page_safe_back_to_event_page()