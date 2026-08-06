
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class Attendance(Task):
    def __init__(self, name="Attendance") -> None:
        super().__init__(name)
        self.attendance_xy = [221, 137] # 主页进入出席簿的按钮位置
        self.left_button_xy_list = [[123, 218], [127, 297]] # 左边要点的两个长期签到位置
        self.collect_button_xy = [1076, 693] # 右下角领取奖励按钮黄色像素位置
     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
     
    def on_run(self) -> None:
        # 进入出席簿
        logging.info(istr({
            CN: "进入统合出席簿",
            EN: "Entering the Attendance page",
        }))
        enter_attandancepage = self.run_until(
            lambda: click(self.attendance_xy, sleeptime=1),
            lambda: Page.is_page(PageName.PAGE_ATTENDANCE),
            times=3
        )
        if not enter_attandancepage:
            logging.error(istr({
                CN: "进入统合出席簿失败",
                EN: "Failed to enter the Attendance page",
            }))
        for i,button_xy in enumerate(self.left_button_xy_list):
            click(button_xy)
            click(button_xy)
            # 可能有蓝色OK解释弹窗
            screenshot()
            click(button_pic(ButtonName.BUTTON_CONFIRMB))
            # 点到这个页面后，点击领取
            success_collect = self.run_until(
                lambda: click(self.collect_button_xy),
                lambda: not match_pixel(self.collect_button_xy, Page.COLOR_BUTTON_YELLOW),
                times=3
            )
            if success_collect:
                logging.info(istr({
                    CN: f"领取第{i+1}个签到奖励成功",
                    EN: f"Successfully collected the {i+1}th attendance reward",
                }))
            self.clear_popup()

     
    def post_condition(self) -> bool:
        return self.back_to_home()