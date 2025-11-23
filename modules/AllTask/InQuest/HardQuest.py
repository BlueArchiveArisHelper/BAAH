from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.RaidQuest import RaidQuest
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, match_pixel, config,
                           screenshot)

from .Questhelper import has_triple_result_event, jump_to_page, close_popup_until_see, quest_has_easy_tab, easy_tab_pos_R, center_tab_pos_L, HARD_TAB_POSITION
import numpy as np


class HardQuest(Task):
    def __init__(self, questlist, name="HardQuest") -> None:
        super().__init__(name)
        self.questlist = questlist

    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_QUEST_SEL)

    def on_run(self) -> None:
        logging.info({"zh_CN": "切换到困难关卡", "en_US": "switch to hard quest"})
        self.run_until(
            lambda: click(HARD_TAB_POSITION),
            lambda: match(button_pic(ButtonName.BUTTON_HARD))
        )
        if config.userconfigdict["HARD_QUEST_EVENT_STATUS"] and not has_triple_result_event():
            logging.warn({"zh_CN": "今天没有开启活动，跳过", "en_US":"Today is not in the activity, skip"})
            return
        # after switch to hard, go to the page
        for each_quest in self.questlist:
            to_page_num = each_quest[0] + 1
            level_ind = each_quest[1]
            repeat_times = each_quest[2]
            if each_quest[-1] == 'false' or each_quest[-1] == False or each_quest[-1] == 0 : # 设置开关关闭
                logging.info(f"{to_page_num}-{level_ind+1}设置为关, 忽略这关扫荡")
                continue
            if repeat_times == 0:
                # if repeat_times == 0, means this quest is not required to do
                continue
            jumpres = jump_to_page(to_page_num)
            if not jumpres:
                logging.error({"zh_CN": "无法到达页面{}, 忽略这关扫荡".format(to_page_num),
                               "en_US": "Cannot jump to page {}, ignore this quest".format(to_page_num)})
                continue
            # clickable points
            logging.info({"zh_CN": "点击从上往下第{}关".format(level_ind+1),
                          "en_US": "Click on level {} from the top down ".format(level_ind+1)})
            ScrollSelect(level_ind, 190, 306, 630, 1116,
                         lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)).run()
            has_easy_tab = quest_has_easy_tab()
            if has_easy_tab:
                # 适配简易攻略，全部服都适配了
                click((385, 183))
            else:
                # 略
                screenshot()
                if not (match(popup_pic(PopupName.POPUP_TASK_INFO)) or match(popup_pic(PopupName.POPUP_TASK_INFO_FANHEXIE))):
                    # 匹配弹窗失败
                    logging.warn({"zh_CN": "未能匹配到扫荡弹窗，跳过", "en_US": "Cannot match the raid popup, skip"})
                    break
            # 扫荡
            RaidQuest(repeat_times, has_easy_tab=has_easy_tab).run()

            # 关闭弹窗，直到看到hard按钮
            close_popup_until_see(button_pic(ButtonName.BUTTON_HARD))
        # 体力不足，也关闭弹窗，直到看到hard按钮
        close_popup_until_see(button_pic(ButtonName.BUTTON_HARD))

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_QUEST_SEL)