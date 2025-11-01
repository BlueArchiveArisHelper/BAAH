from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.AutoAssault.CollectAssaultReward import CollectAssaultReward
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)
from modules.utils.log_utils import logging
from numpy import linspace


class AutoAssault(Task):
    def __init__(self, name="AutoAssault") -> None:
        super().__init__(name)

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def scroll_to_ind(self, target_ind: int) -> None:
        """定位到目标下标关卡的按钮位置"""
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            sleeptime=0.5
        )
        scroll_to_ind = ScrollSelect(target_ind, 159, 293, 597, 1156,
                                     lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE), swipeoffsetx=-200,
                                     finalclick=False)
        scroll_to_ind.run()
        return scroll_to_ind.wantclick_pos

    def check_unlock(self, target_ind: int) -> int:
        """检查下标处的关卡是否解锁了，返回没有解锁的最小下标，返回-1就是target_ind解锁了"""
        res = -1
        # 先直接检查目标下标，如果能有弹窗，说明已经解锁了
        logging.info({"zh_CN": f"检查总力战第{target_ind + 1}关是否解锁",
                      "en_US": f"Check if the {target_ind + 1} level of the Total Assault is unlocked"})
        button_pos = self.scroll_to_ind(target_ind)
        has_popup = self.run_until(
            lambda xy=button_pos: click(xy),
            lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=3,
            sleeptime=0.5
        )
        if has_popup:
            logging.info({"zh_CN": f"检查总力战第{target_ind + 1}关已解锁",
                          "en_US": f"The {target_ind + 1} level of the Total Assault has been unlocked"})
            res = -1
        else:
            # 默认res设置为target_ind（目标下标），既然进入到了这个else，如果0到target_ind-1下标的关卡都没解锁，那么就是target_ind没有解锁了
            res = target_ind
            # 从头开始检查,找到第一个未解锁的关卡
            for ind in range(target_ind):
                # 检查是否解锁
                button_pos = self.scroll_to_ind(ind)
                has_popup = self.run_until(
                    lambda xy=button_pos: click(xy),
                    lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    times=3,
                    sleeptime=0.5
                )
                if not has_popup:
                    res = ind
                    break
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            sleeptime=0.5
        )
        return res

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
        if config.userconfigdict["AUTO_ASSAULT_HELP_STUDENT_IS_SUPPORT"]:
            click((819, 211))
            click((819, 211))
        # 选择要挑选的助战学生
        screenshot()
        helper_stu = match(config.userconfigdict["AUTO_ASSAULT_HELP_STUDENT"], returnpos=True)
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

    def fight_an_assault(self, student_help=False, auto_switch_teams=False):
        """
        点击一个总力战出现弹窗 后接管，打完一次boss后返回总力战页面清除所有弹窗

        @param student_help: 是否需要学生助战
        @param auto_switch_teams: 是否需要自动切换队伍
        """
        # 点击入场按钮,离开总力战页面
        logging.info({"zh_CN": "编辑队伍, 准备出击", "en_US": "Edit team, prepare to attack"})
        self.run_until(
            lambda: click((1018, 526), sleeptime=1.5),
            lambda: not Page.is_page(PageName.PAGE_ASSAULT) or match(popup_pic(PopupName.POPUP_NOTICE)),
        )
        # 如果仍然在总力战页面，说明没有票卷了
        if Page.is_page(PageName.PAGE_ASSAULT) or match(popup_pic(PopupName.POPUP_NOTICE)):
            logging.error({"zh_CN": "总力战未能进入（或是无票卷了），总力战任务结束",
                           "en_US": "Failed to enter the assault (or no tickets left), the assault task is over"})
            return "no_ticket"
        sleep(2)
        # 如果要助战
        if student_help:
            self.select_target_helper()
        # 配队页面点击右下出击按钮
        logging.info({"zh_CN": "出击", "en_US": "sortie"})
        # 这边可能上次打架是个残编队，不会自动切换到下一队，所以需要切换第二队第三队去匹配
        if auto_switch_teams:
            # 如果可能需要切换队伍，那么就试图切换四个队伍
            ypoints = linspace(187, 421, 4)
        else:
            ypoints = [187]
        for ind, yp in enumerate(ypoints):
            # 切换队伍
            logging.info({"zh_CN": f"尝试切换到第{ind + 1}队", "en_US": f"Try switching to the {ind + 1} team"})
            click((122, yp))
            sleep(1)
            open_confirm = self.run_until(
                lambda: click((1157, 662)),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                sleeptime=1,
                times=5,
            )
            if open_confirm:
                break
        # 如果没有打开确认弹窗，那么没有配队
        if not open_confirm:
            if config.userconfigdict["ASSAULT_NO_TEAM_EXCEPT"]:
                raise Exception(istr({
                    EN: "No team can be used, finish task!",
                    CN: "总力战无可用队伍，任务结束!"
                }))
            else:
                logging.warn(istr({
                    EN: "No team can be used",
                    CN: "总力战无可用队伍"
                }))
                self.run_until(
                    lambda: click(Page.TOPLEFTBACK),
                    lambda: Page.is_page(PageName.PAGE_ASSAULT),
                    times = 3,
                    sleeptime = 2
                )
                self.clear_popup()
                return "no_team"
        # 确认 - 跳过演出
        self.run_until(
            lambda: (click(button_pic(ButtonName.BUTTON_CONFIRMB)) or
                     click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.85)) or click((1100, 150)),
            # 这里点MAGICPOINT没反应，点屏幕右边
            lambda: FightQuest.judge_whether_in_fight() and not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=10,
            sleeptime=2,
        )
        logging.info({"zh_CN": "进入到战斗", "en_US": "Enter battle"})
        FightQuest(
            backtopic=lambda: Page.is_page(PageName.PAGE_ASSAULT),
            start_from_editpage=False
        ).run()
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
        )
        return "success"

    def check_if_enter_again(self, next_ind, check_is_open=False):
        """检查顶部是否有再次进入按钮, 如果没有再次进入，就根据check_is_open与否 判断下检查总力战是否开放"""
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
        )
        self.scroll_right_up()
        screenshot()
        if match_pixel((1110, 200), ((250, 225, 137), (255, 230, 145))):
            logging.info({"zh_CN": "检测到再次进入按钮，继续打", "en_US": "Re-entry button detected, continue playing"})
            # 平推一次从上到下数第一个按钮
            pos = (1110, 200)
            canopen_popup = self.run_until(
                lambda: click(pos),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
            if not canopen_popup:
                logging.error({"zh_CN": "尝试打开总力战第{}关时未能匹配到弹窗，总力战任务结束".format(next_ind + 1),
                               "en_US": "Could not match the popup when trying to open the {}th assault, "
                                        "the assault task is over".format(next_ind + 1)})
                return "can_not_open"

            # =================接管战斗=================
            fightres = self.fight_an_assault(auto_switch_teams=True)
            if fightres in ["no_ticket", "no_team"]:
                return fightres
            # 如果这次再次进入战斗了，那么还是得继续检查下
            return self.check_if_enter_again(next_ind)
        elif check_is_open:
            # 如果没有再次进入按钮，那么就检查检查总力战是否开放
            canopen_popup = self.run_until(
                lambda: click((1110, 200)),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
            # 清除弹窗
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            )
            if not canopen_popup:
                logging.error(
                    {"zh_CN": "尝试打开总力战第{}关时未能匹配到弹窗，未开放，总力战任务结束".format(next_ind + 1),
                     "en_US": "Could not match the popup when trying to open the {}th assault, "
                              "not open, the assault task is over".format(
                         next_ind + 1)})
                open_date = ocr_area((788, 474), (1173, 522))[0]
                # 重组数字，去除中文日文什么的
                open_date = "".join([i for i in open_date if i.isdigit() or i in ["/", ":", " "]])
                config.append_noti_sentence(key="ASSAULT_DATE", sentence=istr({
                    CN: f"总力战未开放，下次开放时间: {open_date}",
                    EN: f"Total assault battle is not open, next open time: {open_date}"
                }))
                return "can_not_open"
            else:
                logging.info({"zh_CN": "总力战开放中", "en_US": "Total strength battle is open"})
                end_date = ocr_area((1134, 110), (1253, 136))[0]
                config.append_noti_sentence(key="ASSAULT_DATE", sentence=istr({
                    CN: f"总力战已开放，结束时间: {end_date}",
                    EN: f"Total assault battle is open, end time: {end_date}"
                }))

        else:
            logging.info({"zh_CN": f"总力战第{next_ind + 1}关已完成",
                          "en_US": f"Total Assault level {next_ind + 1} has been completed"})
            return "success"

    def on_run(self) -> None:
        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # 进入总力战
        self.run_until(
            lambda: click((872, 447)) and click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_ASSAULT) or match(button_pic(ButtonName.BUTTON_STORY_MENU)),
        )
        if match(button_pic(ButtonName.BUTTON_STORY_MENU)):
            SkipStory().run()
            # 关闭可能弹窗
            for i in range(5):
                click(Page.MAGICPOINT)

        screenshot()
        # 检查是否到总力战界面
        if not Page.is_page(PageName.PAGE_ASSAULT):
            logging.error({"zh_CN": "未能进入总力战页面，任务结束",
                           "en_US": "Could not enter the assault page, the task is over"})
            return

        target_ind = config.userconfigdict["AUTO_ASSAULT_LEVEL"] - 1
        # =============检查是否有继续打============
        # 顺便检查总力战是否开放
        res = self.check_if_enter_again(0, check_is_open=True)
        if res in ["can_not_open", "no_ticket", "no_team"]:
            CollectAssaultReward().run()
            return
        # 检查所需要的下标是否解锁了
        logging.info({"zh_CN": f"检测总力战第{target_ind + 1}关是否解锁",
                      "en_US": f"Detects whether the {target_ind + 1} level in total battle is unlocked"})
        unlock_level = self.check_unlock(target_ind)
        if unlock_level != -1:
            logging.warn({"zh_CN": f"总力战第{target_ind + 1}关未解锁，最高解锁关卡为第{unlock_level}关",
                          "en_US": f"The {target_ind + 1}th assault is not unlocked, "
                                   f"the highest unlocked assault is the {unlock_level}th assault"})
            next_ind = unlock_level - 1
        else:
            next_ind = target_ind
        while True:
            # 平推一次next_ind
            pos = self.scroll_to_ind(next_ind)
            canopen_popup = self.run_until(
                lambda: click(pos),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
            if not canopen_popup:
                logging.error({"zh_CN": "尝试打开总力战第{next_ind + 1}关时未能匹配到弹窗，总力战任务结束",
                               "en_US": "Could not match the popup when trying "
                                        "to open the {next_ind + 1}th assault, the assault task is over"})
                break
            # 如果一开始解锁的关卡就是目标关卡，那么直接判断能扫荡就扫荡
            if next_ind == target_ind and ocr_area((911, 271), (976, 333))[0] == "1":
                logging.info({"zh_CN": f"总力战第{next_ind + 1}关可以直接扫荡",
                              "en_US": f"Total Assault level {next_ind + 1} can be directly mop-up"})
            else:
                # =================接管战斗=================
                res = self.fight_an_assault(student_help=config.userconfigdict["IS_AUTO_ASSAULT_STUDENT_HELP"])
                if res in ["no_ticket", "no_team"]:
                    break
                # =============检查是否需要继续打============
                res = self.check_if_enter_again(next_ind)
                if res in ["can_not_open", "no_ticket", "no_team"]:
                    break

            # 根据结果判断是否需要平推还是扫荡
            if next_ind == target_ind:
                # 扫荡
                logging.info({"zh_CN": "扫荡总力战第{}关".format(next_ind + 1),
                              "en_US": f"mop-up Total Assault level {next_ind + 1}"})
                button_pos = self.scroll_to_ind(next_ind)
                self.run_until(
                    lambda: click(button_pos),
                    lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    times=2,
                    sleeptime=1
                )
                # 点两次加号
                click((1072, 301))
                click((1072, 301))
                logging.info({"zh_CN": "点击扫荡按钮", "en_US": "Tap the Sweep button"})
                # 点扫荡按钮，直到看到确认
                openswap = self.run_until(
                    lambda: click((939, 398)),
                    lambda: match(button_pic(ButtonName.BUTTON_CONFIRMB)),
                    sleeptime=2
                )
                if not openswap:
                    logging.error({"zh_CN": "未能打开扫荡弹窗，总力战任务结束",
                                   "en_US": "Could not open the sweep popup, the assault task is over"})
                    break
                # 确认
                self.run_until(
                    lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                    lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB))
                )
                # 清除弹窗
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                )
                break
            else:
                # 继续平推
                next_ind += 1
                logging.info({"zh_CN": f"下一关：{next_ind + 1}", "en_US": f"Next Stage: {next_ind + 1}"})
        # 推图结束，领取奖励
        logging.info({"zh_CN": "尝试领取总力战奖励", "en_US": "Try to claim your Total Power Battle rewards"})
        CollectAssaultReward().run()

    def post_condition(self) -> bool:
        return self.back_to_home()
