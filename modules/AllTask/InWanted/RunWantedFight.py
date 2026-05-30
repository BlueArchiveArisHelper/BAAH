 

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

class RunWantedFight(Task):
    def __init__(self, levelnum, runtimes, name="RunWantedFight") -> None:
        """
        after enter the location, start to raid
        
        levelnum start from 0
        """
        super().__init__(name)
        self.levelnum = levelnum
        self.runtimes = runtimes

     
    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_WANTED_SUB, threshold=0.8)
    
    @staticmethod
    def match_task_info() -> bool:
        # 考虑反和谐
        return match(popup_pic(PopupName.POPUP_TASK_INFO)) or match(popup_pic(PopupName.POPUP_TASK_INFO_FANHEXIE))
     
    def on_run(self) -> None:
        rq = RaidQuest(self.runtimes)
        if self.levelnum >= 0:
            # 找到目标关卡点击
            ScrollSelect(self.levelnum, 131, 230, 684, 1118, self.match_task_info).run()
        elif self.levelnum <= -2:
            # 构造tuple的时候会将用户输入-1还原成下标
            # 如果用户GUI填的是-1，那么-1后这里self.levelnum值就是-2. 使用t in range(1, -1, -1)修正为SmartScrollSelect入参代表的值
            # 也就是还原成-1 (第二次循环是-2) 来找到可战斗的倒数第一关（第二关），并且可扫荡（可能最后可战斗的关卡没三星，所以这里需要前推一次）
            for t in range(1, -1, -1):
                SmartScrollSelect(targetind=self.levelnum + t, window_starty=129, window_endy=686, clickx=1079, active_button_color=Page.COLOR_BUTTON_BLUE, hasexpectimage=self.has_popup).run()
                # 如果满足扫荡前提，退出循环
                if rq.pre_condition():
                    logging.info(istr({
                        CN : f"已找到目标可扫荡关卡，开始扫荡",
                        EN : f"Found the target raidable level, start to raid"
                    }))
                    break
                else:
                    logging.warn(istr({
                        CN : f"没有找到目标可扫荡关卡，减少检测下标",
                        EN : f"Did not find the target raidable level, detect index move decrease"
                    }))
                    self.clear_popup()
        else:
            logging.error(istr({
                CN: "关卡序号为0，无法扫荡",
                EN: "Level number is 0, cannot raid"
            }))
            return

        # 扫荡
        rq.run()
        
        # 关闭弹窗，回到WANTED_SUB页面或者WANTED页面
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_WANTED_SUB, threshold=0.8) or Page.is_page(PageName.PAGE_WANTED)
        )
        
        
        
    
     
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_WANTED_SUB, threshold=0.8) or Page.is_page(PageName.PAGE_WANTED)
