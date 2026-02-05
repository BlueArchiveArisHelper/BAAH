from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task

from modules.utils import (click, match_pixel, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config,
                           screenshot, istr, CN, EN)
import numpy as np

class FightQuest(Task):
    """
    进行一次游戏场景内战斗，一般可以从点击任务资讯里的黄色开始战斗按钮后接管

    从编辑部队页面（或剧情播放页面->编辑部队页面）开始，进入到游戏内战斗，然后到战斗结束，离开战斗结算页面

    backtopic: 最后领完奖励回到的页面的匹配逻辑，回调函数
    in_main_story_mode: 是否是在剧情模式下，如果是，那么最后没有奖励页面， 跳过pre判断，直接来到调整三倍速和auto阶段，主线剧情里的战斗有时候无法用右上UI判断进入了战斗
    """

    def __init__(self, backtopic, start_from_editpage=True, in_main_story_mode=False, auto_team=False, name="FightQuest") -> None:
        super().__init__(name)
        self.backtopic = backtopic
        # 是否从编辑部队页面开始，或者直接就是游戏内战斗画面
        self.start_from_editpage = start_from_editpage
        self.in_main_story_mode = in_main_story_mode
        self.click_magic_when_run = False
        self.force_start = in_main_story_mode
        # 编辑页面开始的话，可能有剧情，最多等待2次
        # 如果是从游戏内战斗画面开始，那么不需要等待剧情，所以可以多检测几次
        self.pre_times = 1 if start_from_editpage else 2
        # 是否在选择队伍界面自动配队
        self.auto_team = auto_team
        # 队伍选择界面被选中的队伍的颜色范围
        self.COLOR_TEAM_SELECT_DARK = ([90, 60, 35], [110, 80, 55])
        # 记录战斗结束时是成功还是失败
        self.win_fight_flag = False

    @staticmethod
    def judge_whether_in_fight() -> bool:
        """判断是否进入了小人对战环节，主要是靠判断UI，如果有剧情，就跳过剧情"""
        if match(button_pic(ButtonName.BUTTON_STORY_MENU)):
            SkipStory(pre_times=2).run()
            screenshot()
        return match_pixel((1250, 32), Page.COLOR_BUTTON_WHITE, printit=True)

    def in_edit_team_page(self) -> bool:
        """判断是否在编辑部队页面"""
        count = 0
        for i in range(len(Page.LEFT_FOUR_TEAMS_POSITIONS)):
            if (match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[i], self.COLOR_TEAM_SELECT_DARK) or 
                    match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[i], Page.COLOR_BUTTON_WHITE)):
                count += 1
        return count == 4

    def pre_condition(self) -> bool:
        if self.force_start:
            return True
        if not self.start_from_editpage:
            """
            如果是从游戏内战斗画面开始，那么直接判断右上角白色UI出来就行
            """
            # 等到右上角白色UI出来
            hasUI = self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel((1250, 32), Page.COLOR_BUTTON_WHITE, printit=True),
                times=15,
                sleeptime=2
            )
            if not hasUI:
                # 如果没有UI，尝试跳过剧情
                logging.info({"zh_CN": "检测是否需要跳过剧情", "en_US": "Check if you need to skip the plot"})
                SkipStory(pre_times=2).run()
            else:
                return True
            hasUI2 = self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel((1250, 32), Page.COLOR_BUTTON_WHITE, printit=True),
                times=5,
                sleeptime=2
            )
            return hasUI2
        click(Page.MAGICPOINT, 1)
        click(Page.MAGICPOINT, 1)
        screenshot()
        if Page.is_page(PageName.PAGE_EDIT_QUEST_TEAM):
            return True
        if self.in_edit_team_page():
            return True
        if self.backtopic():
            # 如果已经在战斗结束应当返回的页面，那么直接返回
            return False
        # 可能有剧情
        SkipStory(pre_times=2).run()
        sleep(2)
        return Page.is_page(PageName.PAGE_EDIT_QUEST_TEAM) or self.in_edit_team_page()

    def on_run(self) -> None:
        if not self.force_start:
            if self.start_from_editpage:
                if self.auto_team:
                    # 如果开启了自动配队
                    self.set_auto_team()

                # 点击出击按钮位置
                # 用竞技场的匹配按钮精度不够，点击固定位置即可
                self.run_until(
                    lambda: click((1106, 657)) and click(Page.MAGICPOINT),
                    lambda: not Page.is_page(PageName.PAGE_EDIT_QUEST_TEAM) and not self.in_edit_team_page(),
                    sleeptime=2
                )
            for t in range(2):
                # 等到右上角白色UI出来, 或者可能进入剧情
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match_pixel((1250, 32), Page.COLOR_BUTTON_WHITE) or match(
                        button_pic(ButtonName.BUTTON_STORY_MENU)),
                    times=10,
                    sleeptime=2
                )
                # 1. 如果是白色UI，进入战斗
                if match_pixel((1250, 32), Page.COLOR_BUTTON_WHITE, printit=True):
                    # 战斗中
                    logging.info({"zh_CN": "战斗中...", "en_US": "Fighting"})
                    break
                else:
                    logging.info({"zh_CN": "无法匹配右上暂停", "en_US": "Cannot match the upper right fight pause"})
                    logging.warn({"zh_CN": "请确认游戏设置：战斗时上下黑边 为 关", "en_US": "Please confirm the game settings: Black edges during battle are off"})
                # 2. 如果是剧情，跳过剧情
                if match(button_pic(ButtonName.BUTTON_STORY_MENU)):
                    logging.info({"zh_CN": "剧情中...", "en_US": "In the plot..."})
                    SkipStory(pre_times=3).run()
                    # 跳过剧情后，重新判断是否进入了战斗
                    continue
                else:
                    logging.info({"zh_CN": "无法匹配剧情按钮", "en_US": "Cannot match the story pause button"})
            # 切换AUTO
            logging.info({"zh_CN": "切换AUTO...", "en_US": "Toggle Auto..."})
            self.run_until(
                lambda: click((1208, 658)),
                lambda: not match_pixel((1208, 658), Page.COLOR_BUTTON_GRAY) and match_pixel((1250, 32),
                                                                                             Page.COLOR_BUTTON_WHITE),
                # 直到右上角白色UI出来后右下角按钮也不是灰色时
                times=10,
                sleeptime=2
            )
        else:
            # force start会默认直接进入战斗，主线剧情里的战斗的右上角UI不可用，为灰色
            # 因此切换AUTO逻辑稍微不同
            # 切换AUTO
            logging.info({"zh_CN": "切换AUTO...", "en_US": "Toggle Auto..."})
            # 先点击AUTO保证看到灰色的AUTO按钮，确保进入了战斗
            self.run_until(
                lambda: click((1208, 658)),
                # 直到右下角按钮是灰色时或返回到backtopic
                lambda: match_pixel((1208, 658), Page.COLOR_BUTTON_GRAY) or self.backtopic(),
                times=20,
                sleeptime=2
            )
            # 由于是强制进入，这里也要考虑下其实没有战斗的情况
            if self.backtopic():
                logging.warn({"zh_CN": "已退出关卡战斗页面", "en_US": "Already exited the quest fight page"})
                return
            # 将AUTO打开
            self.run_until(
                lambda: click((1208, 658)),
                lambda: not match_pixel((1208, 658), Page.COLOR_BUTTON_GRAY),  # 直到右下角按钮不是灰色时
                times=3,
                sleeptime=2
            )
        logging.info({"zh_CN": "等待战斗结束...", "en_US": "Waiting for the battle to end..."})
        skip_story = SkipStory()
        # 点魔法点直到战斗结束 或匹配到应当返回的界面，或匹配到story界面
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB)) or match(
                        button_pic(ButtonName.BUTTON_CONFIRMY),
                        threshold=0.8
                    ) or self.backtopic() or skip_story.pre_condition(),
                    times=90,
                    sleeptime=2
        )
        if skip_story.pre_condition():
            skip_story.run()
        if self.backtopic():
            # 此处返回到backtopic，意味着错误进入了战斗
            click(Page.MAGICPOINT)
            click(Page.MAGICPOINT)
            return
        # 结束时如果是黄色确认，那么战斗失败
        if match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8):
            logging.info({"zh_CN": "战斗失败", "en_US": "Fight failed"})
            logging.warn({"zh_CN": "请检查自动AUTO是否开启，提升队伍练度",
                          "en_US": "Please check if AUTO is on, and improve the team's level"})
            self.win_fight_flag = False
        else:
            # 战斗结算页面
            # 四人界面 右下确认蓝色
            logging.info({"zh_CN": "战斗胜利", "en_US": "Victory"})
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB)) and click(Page.MAGICPOINT),
                lambda: not match(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB)),
                times=7,
                sleeptime=1
            )
            self.win_fight_flag = True
        # 战斗后可能剧情
        # 先看有没有出现黄色结算，有结算那肯定没剧情
        hasconfirmy = self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8),
            times=2
        )
        if not hasconfirmy:
            """
            走格子打完boss后的结算的黄色按钮和普通黄色按钮不一样，识别不到，这里如果识别不到普通黄色按钮，就手动点一些那个特殊的黄色按钮位置，然后再判断一次
            """
            click((1010, 666))
            hasconfirmy = self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8),
                times=4,
                sleeptime=2
            )
        if self.backtopic():
            click(Page.MAGICPOINT)
            click(Page.MAGICPOINT)
            return
        # 如果没有黄色确认可能进入剧情
        if not hasconfirmy:
            SkipStory(pre_times=7).run()
        # 如果是主线剧情中的战斗，跳过剧情后，直接回到选择章节页面了
        if self.in_main_story_mode:
            logging.info({"zh_CN": "剧情战斗结束", "en_US": "Plot Battles Ended"})
            # 如果有黄按钮（剧情战斗赢了对局会有蓝按钮，失败情况下只有黄按钮），点击黄按钮确认
            if hasconfirmy:
                self.run_until(
                    lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8) and click(Page.MAGICPOINT),
                    lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMY)),
                    times=7,
                    sleeptime=1
                )
            # 尝试回到backtopic，此处会有 “请见下回” 或 “是否观看下一章节” 的弹窗，等久一点
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                self.backtopic,
                times=15,
                sleeptime=1.5
            )
            return
        # 奖励界面 中下确认黄色
        # 获得奖励，右下确认黄色（左边返回大厅）
        logging.info({"zh_CN": "点击确认...", "en_US": "Click to confirm"})
        backres = self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8) or click(Page.MAGICPOINT),
            self.backtopic,
            times=20,
            sleeptime=1
        )
        logging.info(istr({
            CN: "结束战斗",
            EN: "End of fight"
        }))
        if not backres:
            # 有的关卡点击下方黄色确认后会进入剧情
            # 然后跳过剧情完大部分会直接回到上级页面
            # 部分活动剧情会有强制失败后再进入剧情，这个剧情过完后回到交战结束界面，出现获得物品弹窗，要再点下黄色确认按钮
            SkipStory(pre_times=3).run()
            backto_res = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8) or click(Page.MAGICPOINT),
                self.backtopic
            )
            if not backto_res:
                logging.warn(istr({
                    CN: "未能回到预期界面",
                    EN: "Failed to return to the expected backtopic page"
                }))




    def post_condition(self) -> bool:
        return self.backtopic()