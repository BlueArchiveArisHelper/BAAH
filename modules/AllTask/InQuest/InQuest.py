from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, istr, CN, EN
from .HardQuest import HardQuest
from .NormalQuest import NormalQuest
from .PushQuest import PushQuest
from .OneClickQuest import OneClickQuest
import time
from modules.configs.MyConfig import config


class InQuest(Task):
    """
    进入 普通关卡/困难关卡， types=["normal", "hard", "one-click", "push-normal", "push-hard"]
    """

    def __init__(self, types=[], name="InQuest") -> None:
        super().__init__(name)
        self.types = types

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def on_run(self) -> None:
        # 进入Fight Center
        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # 进入Quest 中心
        self.run_until(
            lambda: click((816, 259)),
            lambda: Page.is_page(PageName.PAGE_QUEST_SEL),
        )
        if "push-normal" in self.types:
            # 判断配置里的PUSH_NORMAL_QUEST长度是否为0
            if config.userconfigdict['PUSH_NORMAL_QUEST'] != 0:
                # do PUSH NORMAL QUEST
                logging.info({"zh_CN": "设置了推普通图任务，开始推图",
                              "en_US": "Set up the task of pushing the normal quest to start the thumbnail"})
                # 序号转下标 章节号
                push_normal_ind = config.userconfigdict['PUSH_NORMAL_QUEST'] - 1
                PushQuest("normal", push_normal_ind,
                          level_ind=config.userconfigdict["PUSH_NORMAL_QUEST_LEVEL"] - 1).run()
            else:
                logging.warn(istr({
                    CN: "未设置推普通图起始的章节关卡!跳过",
                    EN: "The chapter level that starts the normal quest is not set! Skip"
                }))
        if "push-hard" in self.types:
            # 判断配置里的PUSH_HARD_QUEST长度是否为0
            if config.userconfigdict['PUSH_HARD_QUEST'] != 0:
                # do PUSH HARD QUEST
                logging.info({"zh_CN": "设置了推困难图任务，开始推图",
                              "en_US": "Set up the Push Hard Quest task to start pushing the diagram"})
                # 序号转下标，章节号
                push_hard_ind = config.userconfigdict['PUSH_HARD_QUEST'] - 1
                PushQuest("hard", push_hard_ind, level_ind=config.userconfigdict["PUSH_HARD_QUEST_LEVEL"] - 1).run()
            else:
                logging.warn(istr({
                    CN: "未设置推困难图起始的章节关卡!跳过",
                    EN: "The chapter level that starts the hard quest is not set! Skip"
                }))
        # 当天日期
        today = time.localtime().tm_mday
        if "hard" in self.types:
            # 选择一个HARD QUEST List的下标
            if len(config.userconfigdict['HARD']) != 0:
                # 可选任务队列不为空时
                hard_loc = today % len(config.userconfigdict['HARD'])
                # 得到要执行的HARD QUEST LIST
                # [[13,2,3],[19,2,3]]
                hard_list = config.userconfigdict['HARD'][hard_loc]
                # 序号转下标
                hard_list_2 = [[x[0]-1, x[1]-1, *x[2:]] for x in hard_list]
                # do HARD QUEST
                HardQuest(hard_list_2).run()
            else:
                logging.warn(istr({
                    CN: "困难任务队列为空!跳过",
                    EN: "The hard task queue is empty! Skip"
                }))
        if "normal" in self.types:
            # 选择一个NORMAL QUEST List的下标
            if len(config.userconfigdict['NORMAL']) != 0:
                # 可选任务队列不为空时
                normal_loc = today % len(config.userconfigdict['NORMAL'])
                # 得到要执行的NORMAL QUEST LIST
                # [[13,2,3],[19,2,3]]
                normal_list = config.userconfigdict['NORMAL'][normal_loc]
                # do NORMAL QUEST
                # 序号转下标
                normal_list_2 = [[x[0]-1, x[1]-1, *x[2:]] for x in normal_list]
                NormalQuest(normal_list_2).run()
            else:
                logging.warn(istr({
                    CN: "普通任务队列为空!跳过",
                    EN: "The normal task queue is empty! Skip"
                }))
        if "one-click" in self.types:
            # 选择一个ONE CLICK RAID List的下标
            if len(config.userconfigdict['ONE_CLICK_RAID']) != 0:
                # 可选任务队列不为空时
                one_click_loc = today % len(config.userconfigdict['ONE_CLICK_RAID'])
                # 得到要执行的ONE CLICK RAID LIST
                # [[3,10],[4,-1]]
                one_click_list = config.userconfigdict['ONE_CLICK_RAID'][one_click_loc]
                # 序号转下标
                one_click_list_2 = [[x[0]-1, *x[1:]] for x in one_click_list]
                # do ONE CLICK RAID
                OneClickQuest(one_click_list_2).run()
            else:
                logging.warn(istr({
                    CN: "一键任务队列为空!跳过",
                    EN: "The one-click task queue is empty! Skip"
                }))
        self.back_to_home()

    def post_condition(self) -> bool:
        return self.back_to_home()