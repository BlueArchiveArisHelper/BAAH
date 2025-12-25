
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.CollectDailyRewards.CollectDailyRewards import CollectDailyRewards
from modules.AllTask.InQuest.PushQuest import PushQuest
from modules.AllTask.InQuest.Questhelper import quest_has_easy_tab
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class SolveChallenge(Task):
    def __init__(self, name="SolveChallenge") -> None:
        super().__init__(name)
        self.total_completed_num = 0
        self.scroll_down_index = 0

     
    def pre_condition(self) -> bool:
        self.total_completed_num = 0
        self.scroll_down_index = 0
        return self.back_to_home()
        
     
    def on_run(self) -> None:
        # 存储使用简易攻略配置
        whether_use_simple_quest_normal = config.userconfigdict["PUSH_NORMAL_USE_SIMPLE"]
        whether_use_simple_quest_hard = config.userconfigdict["PUSH_HARD_USE_SIMPLE"]
        config.userconfigdict["PUSH_NORMAL_USE_SIMPLE"] = False
        config.userconfigdict["PUSH_HARD_USE_SIMPLE"] = False

        while 1:
            self.back_to_home()
            # 领取所有已完成的挑战任务奖励
            logging.info(istr({
                CN: "领取任务奖励",
                EN: "Collect task rewards"
            }))
            CollectDailyRewards(need_back_home=False).run()
            # 进入每日任务界面
            logging.info(istr({
                CN: "进行挑战任务",
                EN: "Do challenge task"
            }))
            logging.warn(istr({
                CN: "你正在执行清理挑战任务，此任务会持续执行到无挑战任务为止！",
                EN: "This task is clearing the challenge tasks, will keep clearing until no challenge tasks"
            }))
            self.clear_popup()
            # 点击挑战任务
            self.run_until(
                lambda: click((1195, 130)),
                lambda: not match_pixel((1195, 130), Page.COLOR_WHITE)
            )
            # 处理第n个挑战任务
            scroll_task = ScrollSelect(self.scroll_down_index, 153, 285, 625, 1150, hasexpectimage=lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE), swipeoffsetx=-200)
            scroll_task.run()
            if not self.has_popup():
                logging.warn(istr({
                    CN: "无法识别跳转弹窗",
                    EN: "can not recognize popup window"
                }))
                break
            blue_button_pos = scroll_task.wantclick_pos
            click((blue_button_pos[0] + 36, blue_button_pos[1] - 80), sleeptime=3)
            # 等待黑屏跳转,直到魔法点不是黑色像素
            self.run_until(
                lambda: sleep(0.1),
                lambda: not match_pixel(Page.MAGICPOINT, ((0,0,0), (10,10,10))),
                sleeptime=2
            )
            # 通过识别弹窗后右侧像素颜色判断是困难还是普通
            pixel_r = match_pixel((1181,159), ((0,0,50), (30, 30, 80)))
            push_task = PushQuest("hard" if pixel_r else "normal", -1, -1) # 章节和关卡数让PushQuest自己识别弹窗里的
            push_task.start_from_level_popup = True
            push_task.challenge_only = True
            push_task.run()
            if push_task.status == push_task.STATUS_SKIP:
                self.scroll_down_index += 1
                logging.info(istr({
                    CN: "跳过了一个挑战关，挑战任务下标+1",
                    EN: "Since skip this level, challenge level index offset plus 1"
                }))
            else:
                self.total_completed_num += 1
            logging.info(istr({
                CN: f"本次运行已完成{self.total_completed_num}个挑战任务",
                EN: f"{self.total_completed_num} chanllenges are finished"
            }))
        
        # 还原使用简易攻略配置
        config.userconfigdict["PUSH_NORMAL_USE_SIMPLE"] = whether_use_simple_quest_normal
        config.userconfigdict["PUSH_HARD_USE_SIMPLE"] = whether_use_simple_quest_hard
     
    def post_condition(self) -> bool:
        return self.back_to_home()