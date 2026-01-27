
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InEvent.EventStory import EventStory
from modules.AllTask.InEvent.InEvent import InEvent
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task
import numpy as np
from itertools import product
from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class InEventRecap(Task):
    def __init__(self, name="InEventRecap") -> None:
        super().__init__(name)
        self.first_trigger = True
        if "JP" in config.userconfigdict["SERVER_TYPE"]:
            self.event_recap_button = [149, 220] # 日服活动一览放到第二个按钮
        else:
            self.event_recap_button = [149, 136]
        self.COLOR_DARK_BLUE = ([89, 60, 35], [109, 80, 55])
     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    def _go_to_event_recap_page(self) -> bool:
        self.back_to_home()
        self.run_until(
            lambda: click([1049, 558]),
            lambda: not Page.is_page(PageName.PAGE_HOME),
            sleeptime=2
        )
        self.clear_popup()
        goto_res = self.run_until(
            lambda: click(self.event_recap_button),
            lambda: match_pixel(self.event_recap_button, self.COLOR_DARK_BLUE)
        )
        if goto_res and self.first_trigger:
            # 第一次进入时，点击右上角的重新排序按钮
            self.first_trigger = False
            click([1197, 108])
        return goto_res

    def recognize_yellow_points(self, xs, ys, down = False):
        res_list = []
        for y, x in product(ys, xs):
            if match_pixel((x, y + (10 if down else 0)), ([10, 178, 244], [30, 198, 255])):
                res_list.append((x, y))
        return res_list

    def on_run(self) -> None:
        xs = np.linspace(786, 1228, 3, dtype=int)
        ys = np.linspace(155, 502, 3, dtype=int)
        # 是否需要重新进入剧情一览页面
        to_view_page = True
        ine = InEvent()
        for down in range(2):
            logging.info({"zh_CN": "会向下翻页", "en_US": "Will Page down"}) if down else None
            for y, x in product(ys, xs):
                # 是否需要重新进入剧情一览页面
                if to_view_page:
                    if not self._go_to_event_recap_page():
                        logging.error(istr({
                            CN: "无法进入剧情一览页面",
                            EN: "Unable to enter the event recap page",
                        }))
                        return
                    logging.info({"zh_CN": f"进入剧情一览", "en_US": f"Enter event recap"})
                # 判断执行滑动操作
                [self.scroll_right_down(), sleep(2)] if down else None
                [self.scroll_right_up(), sleep(2)] if not down else None
                screenshot()
                logging.info(f"Activate Points:{self.recognize_yellow_points(xs, ys, down)}")
                if match_pixel((x, y + (10 if down else 0)), ([10, 178, 244], [30, 198, 255])):
                    logging.info({"zh_CN": f"当前坐标({x}, {y})有剧情", "en_US": f"Current coordinate ({x}, {y}) has story"})
                    self.run_until(
                        lambda x=x, y=y: click([x-100, y+100]),
                        lambda: not match_pixel(self.event_recap_button, self.COLOR_DARK_BLUE),
                        sleeptime=2
                    )
                    sleep(2)
                    # 点掉剧情提醒的蓝色确认按钮
                    self.run_until(
                        lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                        lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB))
                    )
                    sleep(3)
                    if self.has_popup():
                        SkipStory().run()
                    self.clear_popup()
                    logging.info(istr({
                        CN: "开始执行推剧情任务",
                        EN: "Start executing event story task",
                    }))
                    evtsty = EventStory(max_level=ine.get_biggest_level())
                    evtsty.run()
                    if evtsty.status == Task.STATUS_ERROR:
                        logging.info(istr({
                            CN: "Status_error: 推剧情任务执行失败, 返回",
                            EN: "STATUS_ERROR: Event story task execution failed, returning",
                        }))
                        return
                    to_view_page = True
                else:
                    logging.info({"zh_CN": f"当前坐标({x}, {y})没有剧情", "en_US": f"Current coordinate ({x}, {y}) has no story"})
                    to_view_page = False
                sleep(0.5)

     
    def post_condition(self) -> bool:
        return self.back_to_home()