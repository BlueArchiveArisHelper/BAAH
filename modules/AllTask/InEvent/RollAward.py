
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging
from .EventHelper import from_inner_page_safe_back_to_event_page

class RollAward(Task):
    def __init__(self, name="RollAward") -> None:
        super().__init__(name)
        # 抽奖页面里面的进行抽奖按钮位置
        self.roll_button_xy = [850, 591]

     
    def pre_condition(self) -> bool:
        return super().pre_condition()
    
    def on_run(self) -> None:
        """
        处理活动抽奖页面，从活动主页面进入抽奖页面，点击抽奖按钮对应次数，然后返回活动主页面
        """
        if config.sessiondict["CURRENT_EVENT_ROLL_COUNT"] >= config.userconfigdict["EVENT_ROLL_TARGET_COUNT"]:
            logging.info(istr({
                CN: f"当前抽奖次数 {config.sessiondict['CURRENT_EVENT_ROLL_COUNT']} 已经达到目标次数 {config.userconfigdict['EVENT_ROLL_TARGET_COUNT']}，不再进行抽奖",
                EN: f"Current number of draws {config.sessiondict['CURRENT_EVENT_ROLL_COUNT']} has reached the target number of draws {config.userconfigdict['EVENT_ROLL_TARGET_COUNT']}, no more draws"
            }))
            return
        self.clear_popup()
        roll_page_button_pos = match(config.userconfigdict["EVENT_ENTER_ROLL_PAGE_BUTTON"], returnpos=True)
        if not roll_page_button_pos[0]:
            logging.info(istr({
                CN: f"未能识别抽奖页面入口按钮 {roll_page_button_pos}，跳过抽奖。可能截取的图片已过时？",
                EN: f"Failed to recognize the entrance button of the lottery page {roll_page_button_pos}, skip the lottery. Maybe the captured picture is outdated?"
            }))
            return

        # 点击抽奖页面入口按钮，直到按钮消失
        enter_roll_page = self.run_until(
            lambda: click(config.userconfigdict["EVENT_ENTER_ROLL_PAGE_BUTTON"], sleeptime=2),
            lambda: not match(config.userconfigdict["EVENT_ENTER_ROLL_PAGE_BUTTON"])
        )
        # 判断是否进入抽奖页面
        if not enter_roll_page:
            logging.warn(istr({
                CN: f"点击抽奖页面入口按钮 {config.userconfigdict['EVENT_ENTER_ROLL_PAGE_BUTTON']} 失败，未能进入抽奖页面",
                EN: f"Click the entrance button of the lottery page {config.userconfigdict['EVENT_ENTER_ROLL_PAGE_BUTTON']} failed, failed to enter the lottery page"
            }))
            return
        # 判断按钮是否是亮着的
        sleep(1.5)
        screenshot()
        yellow_button_is_on = match_pixel(self.roll_button_xy, Page.COLOR_BUTTON_YELLOW, printit=True)
        if not yellow_button_is_on:
            logging.warn(istr({
                CN: f"抽奖按钮未亮起，跳过抽奖",
                EN: f"The lottery button is not lit, skip the lottery"
            }))
            return
        # 点击抽奖按钮n次
        def roll_and_collect():
            """点击抽奖，直到出现popup，然后关掉popup"""
            self.clear_popup()
            success_click = self.run_until(
                lambda: click(self.roll_button_xy),
                lambda: self.has_popup()
            )
            self.clear_popup()
            return success_click

        n_times_to_click = config.userconfigdict["EVENT_ROLL_TARGET_COUNT"] - config.sessiondict["CURRENT_EVENT_ROLL_COUNT"]
        for _ in range(n_times_to_click):
            if(roll_and_collect()):
                config.sessiondict["CURRENT_EVENT_ROLL_COUNT"] += 1
                logging.info(istr({
                    CN: f"成功点击抽奖按钮，当前抽奖次数 {config.sessiondict['CURRENT_EVENT_ROLL_COUNT']}",
                    EN: f"Successfully clicked the lottery button, current number of draws {config.sessiondict['CURRENT_EVENT_ROLL_COUNT']}"
                }))
            else:
                logging.warn(istr({
                    CN: f"点击抽奖按钮失败，跳过抽奖",
                    EN: f"Failed to click the lottery button, skip the lottery"
                }))
                break

     
    def post_condition(self) -> bool:
        return from_inner_page_safe_back_to_event_page()