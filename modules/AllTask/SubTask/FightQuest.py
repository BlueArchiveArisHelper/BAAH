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
    """

    def __init__(self, backtopic, start_from_editpage=True, in_main_story_mode=False, auto_team=False, name="FightQuest") -> None:
        super().__init__(name)
        self.backtopic = backtopic
        # 是否在选择队伍界面自动配队
        self.auto_team = auto_team
        # 记录战斗结束时是成功还是失败
        self.win_fight_flag = False
        # 剧情黄色按钮底部高度阈值，与购买弹窗里的黄色按钮区分开
        self.y_height_threshold_story_confirm = 640


    @staticmethod
    def judge_whether_in_story() -> bool:
        """判断是否进入了剧情"""
        return SkipStory().pre_condition()

    @staticmethod
    def judge_whether_in_fight() -> bool:
        """判断是否进入了小人对战环节,用能量条最左边蓝色像素判断"""
        # 判断能量条最左边格子蓝色点
        return match_pixel([831, 694], ([250, 170, 0], [255, 185, 20]), printit=True)
    
    @staticmethod
    def judge_whether_in_edit_team_page() -> bool:
        """判断是否在编辑部队页面"""
        # 队伍选择界面被选中的队伍的颜色范围
        COLOR_TEAM_SELECT_DARK = ([90, 60, 35], [110, 80, 55])
        for i in range(len(Page.LEFT_FOUR_TEAMS_POSITIONS)):
            if match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[i], COLOR_TEAM_SELECT_DARK):
                return True
        return False
    
    def solve_in_edit_team_page(self):
        """处理在编辑部队页面的逻辑"""
        logging.info(istr({
            CN: "检测到在编辑部队页面，准备开始战斗",
            EN: "Detected in the edit team page, preparing to start the fight"
        }))
        if self.auto_team:
            # 如果开启了自动配队
            self.set_auto_team()
        # 点击出击按钮位置
        # 用竞技场的匹配按钮精度不够，点击固定位置即可
        self.run_until(
            lambda: click((1106, 657)) and click(Page.MAGICPOINT),
            lambda: not Page.is_page(PageName.PAGE_EDIT_QUEST_TEAM) and not self.judge_whether_in_edit_team_page(),
            sleeptime=2
        )

    def solve_in_story(self):
        """处理在剧情页面的逻辑"""
        logging.info(istr({
            CN: "检测到在剧情页面，准备跳过剧情",
            EN: "Detected in the story page, preparing to skip the story"
        }))
        SkipStory().on_run()

    def solve_in_fight(self):
        """处理在战斗页面的逻辑"""
        logging.info(istr({
            CN: "检测到在战斗页面，准备进行战斗",
            EN: "Detected in the fight page, preparing to fight"
        }))
        # 切换AUTO
        logging.info({"zh_CN": "切换AUTO...", "en_US": "Toggle Auto..."})
        switch_auto = self.run_until(
            lambda: click((1208, 658)),
            lambda: not match_pixel((1208, 658), Page.COLOR_BUTTON_GRAY),
            # 直到右下角按钮不是灰色时
            times=10,
            sleeptime=2
        )
        if not switch_auto:
            logging.warn(istr({
                CN: "切换AUTO失败",
                EN: "Failed to toggle Auto"
            }))
        # 点魔法点直到战斗结束
        acc_confirm = 0 # 蓝色能量条可能刚好用光，这边确认连续5次匹配不到能量条就结束战斗
        total_confirms = 5
        for i in range(90):
            screenshot()
            if acc_confirm >= total_confirms:
                break
            if self.judge_whether_in_fight():
                acc_confirm = 0
                click(Page.MAGICPOINT)
            else:
                acc_confirm += 1
            sleep(1)
        logging.info(istr({
            CN: "战斗结束，等待结算页面出现",
            EN: "Battle ended, waiting for the settlement page to appear"
        }))
        sleep(3)
        # 等待结算页面出现
        # 点掉蓝色和黄色按钮的逻辑全放在 on_run 事件循环内部
        # 0. 蓝色按钮胜利
        # 1. 黄色按钮失败
        # 2. [940, 644] 走格子打boss后的右下角特殊黄色按钮（左边战斗记录，右边角色立绘）BGR[74, 232, 244]
        # 3. 进入剧情
        # ================
        # 点掉格子boss特殊黄色按钮
        logging.info(istr({
            CN: "准备领取奖励",
            EN: "preparing to claim rewards"
        }))
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB)) or match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8) or self.judge_whether_in_story()
        )
        # 如果是黄色底部确认，标记为失败
        res1 = match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8, returnpos=True)
        if res1[0] and res1[1][1] > self.y_height_threshold_story_confirm:
            # 如果底部黄色确认按钮出现，说明战斗失败
            self.win_fight_flag = False
        else:
            # 否则标记为胜利
            self.win_fight_flag = True
        logging.info(istr({
            CN: f"战斗结果判定完成，结果为: {'胜利' if self.win_fight_flag else '失败'}",
            EN: f"Battle result determination completed, the result is: {'Victory' if self.win_fight_flag else 'Defeat'}"
        }))

    def pre_condition(self) -> bool:
        return True
    
    def on_run(self):
        # 累计两次确认backtopic后退出while
        acc_count = 0
        # 进入事件处理循环
        while(1):
            logging.info(istr({
                CN: "任务事件处理循环中...",
                EN: "In the fight task event handling loop..."
            }))
            screenshot()
            if self.backtopic():
                if acc_count >= 1:
                    break
                else:
                    acc_count += 1
                    sleep(2)
            elif self.judge_whether_in_story():
                self.solve_in_story()
            elif self.judge_whether_in_edit_team_page():
                self.solve_in_edit_team_page()
            elif self.judge_whether_in_fight():
                self.solve_in_fight()
            elif match(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB)):
                # 右下蓝色确认按钮，战斗胜利
                click(button_pic(ButtonName.BUTTON_FIGHT_RESULT_CONFIRMB))
            elif match_pixel([940, 644], ([70, 225, 240], [80, 238, 250])):
                # 走格子打完boss后战斗总结，左侧关卡名称战斗纪录，右侧角色立绘+确认按钮
                click([940, 644])
            elif match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8):
                # 中下或中下偏右黄色确认按钮，战斗失败 或 战斗结算【返回主页/确认】
                res1 = match(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8, returnpos=True)
                # 使用高度判断防止误触点购买弹窗
                if res1[1][1] > self.y_height_threshold_story_confirm:
                    # 底部黄色确认按钮
                    click(button_pic(ButtonName.BUTTON_CONFIRMY))
            # 每一秒判断一次
            click(Page.MAGICPOINT, sleeptime=1)
        # 结束事件处理循环
        logging.info(istr({
            CN: "战斗任务完成，返回任务起始页面",
            EN: "Fight task completed, returning to the starting page"
        }))
        


    def post_condition(self) -> bool:
        return self.backtopic()