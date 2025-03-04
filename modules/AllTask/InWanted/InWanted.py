from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area_0
from modules.utils.log_utils import logging
import time
import numpy as np
from .RunWantedFight import RunWantedFight
from modules.configs.MyConfig import config

class InWanted(Task):
    def __init__(self, name="InWanted") -> None:
        super().__init__(name)



    def pre_condition(self) -> bool:
        if len(config.userconfigdict['WANTED_HIGHEST_LEVEL']) == 0:
            logging.warn({"zh_CN": "没有配置悬赏通缉的level", "en_US" :"There is no level of wanted"})
            return False
        return Page.is_page(PageName.PAGE_HOME)


    def on_run(self) -> None:
        # 得到今天是几号
        today = time.localtime().tm_mday
        # 选择一个location的下标
        target_loc = today % len(config.userconfigdict['WANTED_HIGHEST_LEVEL'])
        target_info = config.userconfigdict['WANTED_HIGHEST_LEVEL'][target_loc]
        # 这之后target_info是一个list，内部会有多个关卡扫荡
        # 判断这一天是否设置有扫荡任务关卡
        if len(target_info) == 0:
            logging.warn({"zh_CN": "今天轮次中无悬赏通缉关卡，跳过",
                          "en_US": "There is no wanted level in today's round, skip"})
            return
        # 序号转下标
        target_info = [[each[0]-1, each[1]-1, *each[2:]] for each in target_info]
        # 从主页进入战斗池页面
        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=5
        )
        # 进入悬赏通缉页面
        caninwanted = self.run_until(
            lambda: click((741, 440)),
            lambda: Page.is_page(PageName.PAGE_WANTED),
            sleeptime=3
        )
        if not caninwanted:
            logging.warn({"zh_CN": "无法打开通缉页面，任务退出", "en_US": "Can't open wanted page, task quit"})
            self.back_to_home()
            return
        # 开始循环扫荡target_info中的每一个关卡
        for each_target in target_info:
            if each_target[-1] == 'false' or each_target[-1] == False or each_target[-1] == 0 : # 开关关闭
                logging.info(f"悬赏通缉{each_target[0]+1}-{each_target[1]+1}设置为关, 忽略")
                continue
            # check whether there is a ticket
            # 使用PageName.PAGE_WANTED的坐标判断是国服还是其他服
            if match(page_pic(PageName.PAGE_WANTED), returnpos=True)[1][1] > 133:
                # 如果右侧Title较低，说明是老版本的国服
                logging.info({"zh_CN": "点击较低的三个定位点", "en_US": "Click on the lower three anchors"})
                points = np.linspace(265, 544, 3)
            else:
                # 可点击的一列点
                points = np.linspace(206, 422, 3)
            # 点击location
            self.run_until(
                lambda: click((959, points[each_target[0]])),
                lambda: Page.is_page(PageName.PAGE_WANTED_SUB),
            )
            # 扫荡对应的level
            RunWantedFight(levelnum = each_target[1], runtimes = each_target[2]).run()
            # 回到SUB界面之后，点击一下返回
            self.run_until(
                lambda: click(Page.TOPLEFTBACK),
                lambda: not Page.is_page(PageName.PAGE_WANTED_SUB),
                sleeptime=3
            )

        self.back_to_home()

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)