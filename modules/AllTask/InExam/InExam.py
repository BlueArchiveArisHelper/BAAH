import numpy as np
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging


# 考试如果队伍数量不够3，需要手动结束考试；如果队伍数量等于3，那么最后一场战斗结束会返回考试区域选择页面
class InExam(Task):
    def __init__(self, name="InExam") -> None:
        super().__init__(name)
        self.ENTER_EXAM = [1052, 450]
        # 三个考试地区的判断点
        self.AREAS_POINTS = [
            [102, 375],
            [635, 394],
            [1030, 366]
        ]
        self.COLOT_GIVEUP_POINT = {"pos": [1100, 669], "color":([220, 210, 200], [255, 255, 235])}
        # 入场四个按钮
        y_list = np.linspace(189, 482, 4, dtype=int)
        self.enter_buttons_pos_list = [(1145, y) for y in y_list]
        # 扫荡按钮
        self.COLOR_RAID_POINT = {"pos": [783, 669], "color": ([245, 200, 100], [255, 240, 130])}


    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    def select_target_helper(self) -> None:
        """选择助战的学生"""
        logging.info({"zh_CN": "选择助战学生", "en_US": "choose helper students"})
        self.run_until(
            lambda: click((1197, 166)),
            lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            sleeptime=2
        )
        # 弹出调整编队弹窗后，点击助力者按钮
        click((1197, 166))
        click((1197, 166))
        # 点击支援按钮
        if config.userconfigdict["EXAM_HELP_STUDENT_IS_SUPPORT"]:
            click((750, 211))
            click((750, 211))
        # 选择要挑选的助战学生
        screenshot()
        helper_stu = match(config.userconfigdict["EXAM_HELP_STUDENT"], returnpos=True)
        if helper_stu[0]:
            clickpos = helper_stu[1]
            # 点击助战学生
            logging.info({"zh_CN": "点击助战学生", "en_US": "Tap the assisting student"})
            click(clickpos)
            sleep(1)
            # 点击右下角确认按钮
            # 点击蓝色确认按钮直到清除弹窗
            select_helper = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)) or click((1143, 592)),
                lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                sleeptime=1.5
            )
            if select_helper:
                logging.info({"zh_CN": "选择助战学生成功", "en_US": "Successfully selected a helper student"})
            else:
                logging.warn({"zh_CN": "选择助战学生失败，将不会选择助战学生",
                              "en_US": "Failed to select a helper student, no helper student will be selected"})
                click(Page.MAGICPOINT)
                screenshot()
        else:
            logging.warn({"zh_CN": "未找到助战学生，将不会选择助战学生",
                          "en_US": "Did not find a helper student, no helper student will be selected"})
            click(Page.MAGICPOINT)
            screenshot()

    
    def do_a_new_exam(self) -> bool:
        """开始新的一次考试，返回是否存在至少一个队伍成功"""
        all_lose = True
        # 按钮位置相同
        self.run_until(
            lambda: click(self.COLOT_GIVEUP_POINT["pos"]),
            lambda: self.has_popup()
        )
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY)),
            lambda: not self.has_popup()
        )
        target_team_number = int(config.userconfigdict["EXAM_TEAM_COUNT"])
        target_level = int(config.userconfigdict["EXAM_TARGET_LEVEL"])
        try_lower_level = bool(config.userconfigdict["EXAM_ALLOW_FALLBACK"])
        use_student_help = bool(config.userconfigdict["IS_EXAM_STUDENT_HELP"])
        for t in range(target_team_number):
            current_level = target_level
            while current_level >= 1:
                self.clear_popup()
                target_ind = current_level - 1
                logging.info(istr({
                    CN: f"正在进行考试，选择第{current_level}关",
                    EN: f"Exam in progress, select level {current_level}",
                }))
                # 点第n关
                self.run_until(
                    lambda: click(self.enter_buttons_pos_list[target_ind]),  # 点击第n个按钮，下标减一
                    lambda: self.has_popup()
                )
                # 点考试开始
                self.run_until(
                    lambda: click([639, 508]),
                    lambda: not self.has_popup()
                )
                # =====配队页面=======
                # 切队伍
                self.run_until(
                    lambda: click(Page.LEFT_FOUR_TEAMS_POSITIONS[t]),
                    lambda: match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[t], Page.COLOR_SELECTED_LEFT_FOUR_TEAM)
                )
                # 选择助战学生
                if use_student_help:
                    self.select_target_helper()
                    use_student_help = False # 只选一次助战学生
                # 出击打架
                self.run_until(
                    lambda: (click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.8) or click((1106, 657))),
                    lambda: not Page.is_page(PageName.PAGE_EXAM),
                    sleeptime=2
                )
                team_fight = FightQuest(backtopic=lambda: Page.is_page(PageName.PAGE_EXAM),
                                        start_from_editpage=False)
                team_fight.run()
                self.clear_popup()
                if not team_fight.win_fight_flag:
                    logging.warn(istr({
                        CN: f"考试队伍 {t+1} 第 {current_level} 关考试失败",
                        EN: f"Exam team {t+1} failed level {current_level}",
                    }))
                    if try_lower_level:
                        current_level -= 1 # 降低难度
                        if current_level >= 1:
                            logging.info(istr({
                                CN: f"尝试挑战低一档难度",
                                EN: f"Attempt to challenge a lower level",
                            }))
                        else:
                            logging.warn(istr({
                                CN: f"考试队伍 {t+1} 从 {target_level} 到 1 的所有难度均失败，请检查配队",
                                EN: f"Exam team {t+1} has failed all attempted levels from {target_level} to 1, please check your team configuration",
                            }))
                    else:
                        break
                else:
                    logging.info(istr({
                        CN: f"考试队伍 {t+1} 第 {current_level} 关考试通过",
                        EN: f"Exam team {t+1} passed level {current_level}",
                    }))
                    all_lose = False
                    break  # 挑战成功，换下一个队伍
        # 队伍交战完毕，如果队伍数量小于3，会停留在考试关卡页面，需要判断点击放弃按钮
        self.finish_last_exam()
        return not all_lose

    def can_exam_raid(self):
        screenshot()
        if match_pixel(self.COLOR_RAID_POINT["pos"], self.COLOR_RAID_POINT["color"]):
            # 扫荡按钮亮了
            logging.info(istr({
                CN: "存在扫荡按钮",
                EN: "Raid button exists",
            }))
            return True
        logging.info(istr({
            CN: "不存在扫荡按钮",
            EN: "Raid button not found",
        }))
        return False

    def do_exam_raid(self):
        # 进行考试扫荡
        open_raid_popup = self.run_until(
            lambda: click(self.COLOR_RAID_POINT["pos"]),
            lambda: self.has_popup()
        )
        if not open_raid_popup:
            # 扫荡弹窗没有
            logging.warn(istr({
                CN: "扫荡弹窗没打开",
                EN: "Raid popup not found",
            }))
            return False
        # 按 + 号
        click([991, 359])
        click([991, 359])
        click([991, 359])
        click([991, 359])
        # 如果弹窗消失，则没有考试票卷了
        screenshot()
        if not self.has_popup():
            logging.warn(istr({
                CN: "扫荡弹窗消失，可能是没有考试卷了，扫荡结束",
                EN: "No exam tickets, raid end",
            }))
            return
        # 点击扫荡
        self.run_until(
            lambda: click([897, 465]),
            lambda: match(button_pic(ButtonName.BUTTON_CONFIRMB))
        )
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
            lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB))
        )
        self.clear_popup()

    def go_to_open_exam_area_pos(self) -> bool:
        """点击并进入开放考试的区域，返回是否成功进入，如果没有开放区域，返回False"""
        screenshot()
        if match_pixel([370, 681], Page.COLOR_WHITE):
            # 考试关卡选择页面
            logging.info(istr({
                CN: "已经在考试关卡选择页面",
                EN: "Already in exam level selection page",
            }))
            return True
        else:
            # 地区选择
            # 判断地区选择页面左上角是否有助人设定
            if match_pixel([57, 91], Page.COLOR_BUTTON_WHITE):
                self.AREAS_POINTS[0] = [82, 438]
                logging.info(istr({
                    CN: f"检测到助人设定，调整考试区域坐标，当前坐标为{self.AREAS_POINTS}",
                    EN: f"Detected helper settings, adjusted exam area coordinates, current coordinates are {self.AREAS_POINTS}",
                }))
            # 判断开放的考试区域
            can_enter = False
            for i in range(len(self.AREAS_POINTS)):
                if match_pixel(self.AREAS_POINTS[i], Page.COLOR_WHITE):
                    # 亮的区域
                    can_enter = True
                    # 进入考试,下方出现白色bar
                    self.run_until(
                        lambda: click([self.AREAS_POINTS[i][0] + 50, self.AREAS_POINTS[i][1]]),
                        lambda: match_pixel([370, 681], Page.COLOR_WHITE)
                    )
                    logging.info(istr({
                        CN: "进入考试区域",
                        EN: "Enter exam area",
                    }))
                    return True
            logging.info(istr({
                CN: "没有可进入的考试区域",
                EN: "No available exam area",
            }))
            return False
    
    def finish_last_exam(self):
        """放弃未完成的考试，会判断是否右下角有放弃按钮点击"""
        screenshot()
        if match_pixel(self.COLOT_GIVEUP_POINT["pos"], self.COLOT_GIVEUP_POINT["color"]):
            # 结束上次的考试
            logging.info(istr({
                CN: "结束上次的考试",
                EN: "End the last exam",
            }))
            self.run_until(
                lambda: click(self.COLOT_GIVEUP_POINT["pos"]),
                lambda: self.has_popup()
            )
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB))
            )
            sleep(2)
            self.clear_popup()
        else:
            logging.info(istr({
                CN: "不存在放弃按钮",
                EN: "No give up button",
            }))
        
     
    def on_run(self) -> None:
        # 进到中心
        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # =====进入综合战术测试/合同火力演习======
        self.run_until(
            lambda: click(self.ENTER_EXAM),
            lambda: not Page.is_page(PageName.PAGE_FIGHT_CENTER),
        )
        self.clear_popup()
        # 第一次可能有剧情
        story = SkipStory()
        if story.pre_condition():
            story.on_run()
            self.clear_popup()
        # 两个页面，一个是地区选择，一个是考试选择
        if not self.go_to_open_exam_area_pos():
            # 考试未开放，返回
            return
        # ======考试选择页面=======
        # 上次考试可能没结束，点结束上次的
        self.finish_last_exam()
        self.clear_popup()
        if not self.can_exam_raid():
            # 开始新考试
            has_team_passed = self.do_a_new_exam()
            if not has_team_passed:
                logging.error(istr({
                    CN: "考试全部队伍失败,无法扫荡，请降低考试关卡难度或提高队伍练度",
                    EN: "All exam teams failed， please lower the exam level or increase the team level",
                }))
                return
            else:
                logging.info(istr({
                    CN: "考试结束",
                    EN: "Exam finished",
                }))
        # 考试扫荡，如果是交战结束后，那么会回到考试区域选择页面，重新进入下
        self.go_to_open_exam_area_pos()
        self.do_exam_raid()
            

            

     
    def post_condition(self) -> bool:
        return self.back_to_home()