 

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.RaidQuest import RaidQuest
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect, SmartScrollSelect
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, istr, CN, EN

import numpy as np
from modules.utils.log_utils import logging


class RunExchangeFight(Task):
    def __init__(self, levelnum, runtimes, name="RunExchangeFight") -> None:
        """
        after enter the location, start to raid
        
        levelnum start from 0
        """
        super().__init__(name)
        self.levelnum = levelnum
        self.runtimes = runtimes

     
    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_EXCHANGE_SUB)
    
    @staticmethod
    def match_task_info() -> bool:
        # 任务信息弹窗
        return match(popup_pic(PopupName.POPUP_TASK_INFO)) or match(popup_pic(PopupName.POPUP_TASK_INFO_FANHEXIE))
     
    def on_run(self) -> None:
        rq = RaidQuest(self.runtimes)
        if self.levelnum > 0:
            # 找到目标关卡点击
            ScrollSelect(self.levelnum, 134, 235, 682, 1115, self.match_task_info).run()
        elif self.levelnum < 0:
            for t in range(1, -1, -1):
                SmartScrollSelect(targetind=self.levelnum + t, window_starty=129, window_endy=686, clickx=1079, active_button_color=Page.COLOR_BUTTON_BLUE, hasexpectimage=self.has_popup).run()
                if rq.pre_condition():
                    logging.info(istr({
                        CN: f"已找到目标可扫荡关卡，开始扫荡",
                        EN: f"Found the target raidable level, start to raid"
                    }))
                    break
                else:
                    logging.warn(istr({
                        CN: f"没有找到目标可扫荡关卡，减少检测下标",
                        EN: f"Did not find the target raidable level, detect index move decrease"
                    }))
                    self.clear_popup()


        # 扫荡
        rq.run()
        # 关闭弹窗，回到EXCHANGE_SUB页面
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_EXCHANGE_SUB) or Page.is_page(PageName.PAGE_EXCHANGE)
        )
        
        
        
    
     
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_EXCHANGE_SUB) or Page.is_page(PageName.PAGE_EXCHANGE)
