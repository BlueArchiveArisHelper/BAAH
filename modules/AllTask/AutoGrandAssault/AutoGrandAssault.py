from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.AutoGrandAssault.CollectGrandAssaultReward import CollectGrandAssaultReward
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)
from modules.utils.log_utils import logging
from numpy import linspace
import re


class AutoGrandAssault(Task):
    def __init__(self, name="AutoGrandAssault") -> None:
        super().__init__(name)

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def enter_grand_assault_zone(self, zone_name: str, zone_pos: tuple) -> bool:
        """
        进入指定的大决战区域（左/中/右）
        @param zone_name: 区域名称（左/中/右）
        @param zone_pos: 区域坐标
        @return: 是否成功打开弹窗
        """
        logging.info({"zh_CN": f"进入{zone_name}区域", "en_US": f"Enter {zone_name} zone"})
        
        # 点击区域，直到匹配到大决战大厅按钮
        canopen_popup = self.run_until(
            lambda: click(zone_pos),
            lambda: match(button_pic(ButtonName.BUTTON_GRAND_ASSAULT_LOBBY)),
            times=2,
            sleeptime=1
        )
        
        if not canopen_popup:
            logging.error({"zh_CN": f"尝试打开{zone_name}区域时未能匹配到大厅按钮",
                          "en_US": f"Failed to match lobby button when opening {zone_name} zone"})
            return False
        
        return True
    
    def back_to_zone_selection(self) -> None:
        """
        点击左上角返回区域选择界面
        """
        logging.info({"zh_CN": "返回区域选择界面", "en_US": "Back to zone selection"})
        # 先魔法点两下
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=2,
            sleeptime=0.5
        )
        # 点击左上角返回按钮，直到匹配不到大决战大厅按钮
        self.run_until(
            lambda: click((133, 98)),
            lambda: not match(button_pic(ButtonName.BUTTON_GRAND_ASSAULT_LOBBY)),
            times=3,
            sleeptime=1
        )
    
    def check_if_enter_again_grand_assault(self, target_level: int, is_recursive: bool = False) -> str:
        """
        检查大决战区域是否有再次入场按钮（黄色/橙色按钮）
        如果有则继续战斗，直到没有再次入场按钮为止
        @param target_level: 目标关卡等级
        @param is_recursive: 是否是战斗后的递归检查（区分首次无再次入场/战斗后无再次入场）
        @return: 
            "success" 首次检查无再次入场，
            "success_after_battle" 战斗后无再次入场，
            "no_ticket" 票卷不足，
            "no_team" 无队伍/炸票，
            "can_not_open" 无法打开
        """
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
        )
        
        # 滑动到右上角查看是否有再次入场按钮
        self.scroll_right_up()
        screenshot()
        
        # 检测再次入场按钮的颜色（黄色/橙色区域）
        if match_pixel((1110, 200), ((250, 225, 137), (255, 230, 145))):
            logging.info({"zh_CN": "检测到再次入场按钮，继续战斗", "en_US": "Re-entry button detected, continue fighting"})
            
            # 点击进入再次入场
            pos = (1110, 200)
            canopen_popup = self.run_until(
                lambda: click(pos),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
            
            if not canopen_popup:
                logging.error({"zh_CN": f"尝试打开第{target_level}关再次入场时未能匹配到弹窗",
                              "en_US": f"Failed to match popup when opening level {target_level} re-entry"})
                return "can_not_open"
            
            # 执行战斗
            fight_result = self.fight_a_grand_assault(auto_switch_teams=True)
            
            if fight_result == "fight_no_ticket":
                logging.error({"zh_CN": "再次入场战斗票卷不足",
                              "en_US": "Not enough tickets for re-entry battle"})
                return "no_ticket"
            elif fight_result == "fight_no_team":
                logging.error({"zh_CN": "再次入场战斗无可用队伍",
                              "en_US": "No available team for re-entry battle"})
                return "no_team"
            
            # 战斗后递归检查再次入场（标记为递归调用）
            return self.check_if_enter_again_grand_assault(target_level, is_recursive=True)
        
        else:
            if is_recursive:
                # 战斗后无再次入场，返回专属状态
                logging.info({"zh_CN": f"战斗后无再次入场，需要返回大厅执行扫荡",
                             "en_US": f"No re-entry after battle, need to return to lobby for sweep"})
                return "success_after_battle"
            else:
                # 首次检查无再次入场，按原逻辑返回
                logging.info({"zh_CN": f"当前无再次入场",
                             "en_US": f"Now no re-entry"})
                return "success"

    def scroll_to_target_level(self, target_level: int) -> None:
        """定位到目标下标关卡的按钮位置"""
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            sleeptime=0.5
        )
        scroll_to_ind = ScrollSelect(target_level - 1, 159, 293, 597, 1156,
                                     lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE), swipeoffsetx=-200,
                                     finalclick=False)
        scroll_to_ind.run()
        return scroll_to_ind.wantclick_pos
    
    def fight_a_grand_assault(self, auto_switch_teams=False):
        """
        点击一个大决战出现弹窗 后接管，打完一次boss后返回总力战页面清除所有弹窗
        @param auto_switch_teams: 是否需要自动切换队伍
        @return: "fight_finished" 战斗结束，"fight_no_ticket" 票卷不足，"fight_no_team" 无队伍/炸票
        """
        # 点击入场按钮,离开总力战页面
        logging.info({"zh_CN": "编辑队伍, 准备出击", "en_US": "Edit team, prepare to attack"})
        self.run_until(
            lambda: click((1018, 526), sleeptime=1.5),
            lambda: not match(button_pic(ButtonName.BUTTON_GRAND_ASSAULT_LOBBY)) or match(popup_pic(PopupName.POPUP_NOTICE)),
        )
        # 如果仍然在大决战页面，说明没有票卷了
        if match(button_pic(ButtonName.BUTTON_GRAND_ASSAULT_LOBBY)):
            logging.error({"zh_CN": "大决战未能进入（或是无票卷了），结束",
                           "en_US": "Failed to enter grand assault (or no tickets left), over"})
            return "fight_no_ticket"
        sleep(2)
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
            if config.userconfigdict["GRAND_ASSAULT_NO_TEAM_EXCEPT"]:
                raise Exception(istr({
                    EN: "No team can be used, finish task!",
                    CN: "大决战无可用队伍，任务结束!"
                }))
            else:
                logging.warn(istr({
                    EN: "No team can be used",
                    CN: "大决战无可用队伍"
                }))
                # 点击左上角返回，直到返回到大决战关卡页面
                self.run_until(
                    lambda: click(Page.TOPLEFTBACK),
                    lambda: match(button_pic(ButtonName.BUTTON_GRAND_ASSAULT_LOBBY)),
                    times = 3,
                    sleeptime = 2
                )
                self.clear_popup()
            
            logging.info({"zh_CN": "点击再次入场按钮", "en_US": "Tap re-entry button"})
            can_enter_again = self.run_until(
                    lambda: click((1110, 200)),
                    lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    times=2,
                    sleeptime=1
                )
                
            if can_enter_again:
                    # 点击 [840, 538] 终止再次入场
                    logging.info({"zh_CN": "终止再次入场", "en_US": "Terminate re-entry"})
                    click((840, 538))
                    sleep(1)
                    # 点击蓝色确定
                    click((771, 504))
                    sleep(1)
                    
                    # 清除可能的弹窗
                    self.run_until(
                        lambda: click(Page.MAGICPOINT),
                        lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                        sleeptime=0.5
                    )
            return "fight_no_team"
        # 确认 - 跳过演出
        self.run_until(
            lambda: (click(button_pic(ButtonName.BUTTON_CONFIRMB)) or
                     click(button_pic(ButtonName.BUTTON_CONFIRMY), threshold=0.85)) or click((1100, 150)),
            lambda: FightQuest.judge_whether_in_fight() and not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=15,
            sleeptime=2,
        )
        logging.info({"zh_CN": "进入到战斗", "en_US": "Enter battle"})
        FightQuest(
            backtopic=lambda: Page.is_page(PageName.PAGE_GRAND_ASSAULT),
            start_from_editpage=False
        ).run()
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
        )
        return "fight_finished"

    def check_and_raid_quest(self, target_level: int) -> str:
        """
        检查指定关卡是否可以扫荡，如果可以则执行扫荡
        参照总力战的扫荡逻辑：先滑动到目标关卡，然后根据 OCR 识别结果决定行动
        @param target_level: 目标关卡等级（1-based）
        @return: "success" 成功扫荡，"no_raid_button" 不存在扫荡按钮/未解锁，"no_ticket" 无票卷，"need_battle" 需要战斗
        """

        logging.info({"zh_CN": f"检查关卡 {target_level} 是否可以扫荡",
                     "en_US": f"Check if level {target_level} can be swept"})
        
        # 先滑动到目标关卡位置，获取按钮坐标
        button_pos = self.scroll_to_target_level(target_level)
        
        if not button_pos:
            logging.error({"zh_CN": f"无法滑动到第{target_level}关",
                          "en_US": f"Cannot scroll to level {target_level}"})
            return "no_raid_button"
        
        # 点击目标关卡按钮打开弹窗
        canopen_popup = self.run_until(
            lambda xy=button_pos: click(xy),
            lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=2,
            sleeptime=1
        )
        
        if not canopen_popup:
            logging.error({"zh_CN": f"无法打开第{target_level}关的弹窗，可能未解锁",
                          "en_US": f"Cannot open popup for level {target_level}, may be locked"})
            return "no_raid_button"
        
        # 检查扫荡次数
        raid_count_text = ocr_area((911, 271), (976, 333))[0]
        logging.info({"zh_CN": f"识别到的扫荡次数文本：{raid_count_text}",
                     "en_US": f"Recognized raid count text: {raid_count_text}"})
        
        # 根据识别的数字决定行动
        if raid_count_text == "0":
            # 票卷耗尽
            logging.warn({"zh_CN": f"第{target_level}关票卷已耗尽（次数：{raid_count_text}），跳过",
                         "en_US": f"Level {target_level} tickets exhausted (count: {raid_count_text}), skip"})
            # 关闭弹窗
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                sleeptime=0.5
            )
            return "no_ticket"
        
        elif raid_count_text == "1":
            # 直接扫荡
            logging.info({"zh_CN": f"第{target_level}关可以直接扫荡",
                         "en_US": f"Level {target_level} can be directly swept"})
            # 点两下加号，日服目前会直接点Max
            click((1072, 301))
            click((1072, 301))
            sleep(0.5)
            
            # 点击扫荡按钮，直到看到确定
            logging.info({"zh_CN": "点击扫荡按钮", "en_US": "Tap sweep button"})
            openswap = self.run_until(
                lambda: click((939, 398)),
                lambda: match(button_pic(ButtonName.BUTTON_CONFIRMB)),
                sleeptime=2,
                times=5
            )
            
            # 点击确认按钮执行扫荡
            logging.info({"zh_CN": "确认扫荡", "en_US": "Confirm sweep"})
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB)),
                sleeptime=2
            )
            if not openswap:
                logging.error({"zh_CN": "未能打开扫荡弹窗",
                              "en_US": "Could not open sweep popup"})
                # 关闭弹窗
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    sleeptime=0.5
                )
                return "no_raid_button"
            
            # 清除可能的奖励弹窗
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                sleeptime=0.5
            )
            
            logging.info({"zh_CN": f"第{target_level}关扫荡完成",
                         "en_US": f"Level {target_level} sweep completed"})
            return "success"
        
        else:
            # 次数不是 0 或 1，需要战斗
            logging.info({"zh_CN": f"第{target_level}关需要战斗（次数：{raid_count_text}）",
                         "en_US": f"Level {target_level} requires battle (count: {raid_count_text})"})
            ## 如果GRAND_ASSAULT_NO_FIGHT开启，不进行战斗直接回大厅去下一个区域任务
            if config.userconfigdict["GRAND_ASSAULT_NO_FIGHT"]:
                logging.info({"zh_CN": f"设置大决战不进行战斗，返回大厅",
                              "en_US": f"Grand Assault has been set not to fight, skip the fight."})
                return "no_raid_button"
            
            # 关闭弹窗
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                sleeptime=0.5
            )
            
            # 重新点击进入战斗
            canopen_popup = self.run_until(
                lambda xy=button_pos: click(xy),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
            
            if not canopen_popup:
                logging.error({"zh_CN": f"无法再次打开第{target_level}关的弹窗",
                              "en_US": f"Cannot open popup for level {target_level} again"})
                return "no_raid_button"
            
            # 执行战斗
            logging.info({"zh_CN": "点击进入战斗", 
                          "en_US": "Tap to enter battle"})
            fight_result = self.fight_a_grand_assault(auto_switch_teams=False)
            
            if fight_result == "fight_finished":
                return "need_battle"  # 战斗成功，需要重新检查扫荡
            elif fight_result == "fight_no_ticket":
                logging.error({"zh_CN": "战斗票卷不足",
                              "en_US": "Not enough tickets during battle"})
                return "no_ticket"
            elif fight_result == "fight_no_team":
                logging.error({"zh_CN": "无可用队伍",
                             "en_US": "No available team"})
                return "no_team"
            else:
                return "no_raid_button"

    def on_run(self) -> None:
        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # 进入大决战
        self.run_until(
            lambda: click((1131, 447)) and click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_GRAND_ASSAULT) or match(button_pic(ButtonName.BUTTON_STORY_MENU)),
        )
        if match(button_pic(ButtonName.BUTTON_STORY_MENU)):
            SkipStory().run()
            # 关闭可能弹窗
            for i in range(5):
                click(Page.MAGICPOINT)

        screenshot()
        # 检查是否到大决战战界面
        if not Page.is_page(PageName.PAGE_GRAND_ASSAULT):
            logging.error({"zh_CN": "未能进入大决战页面，任务结束",
                           "en_US": "Could not enter the grand assault page, the task is over"})
            return
        
        # 处理再次入场按钮逻辑
        if match_pixel((1110, 200), ((250, 225, 137), (255, 230, 145))):
            logging.info({"zh_CN": "检测到再次入场按钮，结束再次入场", "en_US": "Re-entry button detected, end re-entry"})
            can_enter_again = self.run_until(
                lambda: click((1110, 200)),
                lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                times=2,
                sleeptime=1
            )
                
            if can_enter_again:
                # 点击 [840, 538] 终止再次入场
                logging.info({"zh_CN": "终止再次入场", "en_US": "Terminate re-entry"})
                click((840, 538))
                sleep(1)
                # 点击蓝色确定
                click((771, 504))
                sleep(1)
                
                # 清除可能的弹窗
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    sleeptime=0.5
                )
            # 要进行一次回到大决战主页的操作
                self.back_to_zone_selection()
                sleep(1)
        # 回到主页以后先OCR识别日期文本
        screenshot()
        date_text = ocr_area((860, 670), (1080, 690))[0]
        # 重组数字，去除中文日文什么的
        date_text = "".join([i for i in date_text if i.isdigit() or i in ["/", ":", " ", "~", "-"]])
        logging.info({"zh_CN": f"识别到的大决战日期：{date_text}",
                     "en_US": f"Recognized date text of grand assault: {date_text}"})
        # 标记是否成功进入过区域（用于判断以通知大决战是否开放）
        has_entered_zone = False
        # 定义三个区域的坐标和配置
        zones = {
            "left": {
                "name": {"zh_CN": "左", "en_US": "Left"},
                "pos": (368, 310),
                "config_key": "AUTO_GRAND_ASSAULT_LEFT_LEVEL"
            },
            "middle": {
                "name": {"zh_CN": "中", "en_US": "Middle"},
                "pos": (667, 431),
                "config_key": "AUTO_GRAND_ASSAULT_MIDDLE_LEVEL"
            },
            "right": {
                "name": {"zh_CN": "右", "en_US": "Right"},
                "pos": (966, 238),
                "config_key": "AUTO_GRAND_ASSAULT_RIGHT_LEVEL"
            }
        }
        
        # 依次处理三个区域，单个区域完成战斗+扫荡闭环后再处理下一个
        for zone_key, zone_info in zones.items():
            logging.info({"zh_CN": f"开始处理{zone_info['name']['zh_CN']}区域",
                         "en_US": f"Start processing {zone_info['name']['en_US']} zone"})
            
            target_level = config.userconfigdict.get(zone_info["config_key"], 1)
            logging.info({"zh_CN": f"{zone_info['name']['zh_CN']}区域目标关卡：{target_level}",
                         "en_US": f"{zone_info['name']['en_US']} zone target level: {target_level}"})
            
            # 单个区域的循环：战斗→返回→重新进入→扫荡
            zone_processed = False
            while not zone_processed:
                # 进入当前区域
                if not self.enter_grand_assault_zone(zone_info['name']['zh_CN'], zone_info["pos"]):
                    logging.error({"zh_CN": f"无法进入{zone_info['name']['zh_CN']}区域，可能未开放",
                                  "en_US": f"Cannot enter {zone_info['name']['en_US']} zone, may not be opened"})
                    zone_processed = True
                    continue
                has_entered_zone = True
                # ========== 再次入场逻辑处理 ==========
                # 先检查是否有再次入场
                reentry_result = self.check_if_enter_again_grand_assault(target_level)

                if reentry_result in ["no_team","no_ticket", "can_not_open"]:
                    logging.warn({"zh_CN": f"{zone_info['name']['zh_CN']}区域再次入场处理失败（{reentry_result}），跳过再次入场",
                                 "en_US": f"{zone_info['name']['en_US']} zone re-entry processing failed ({reentry_result}), skip re-entry"})
                    self.back_to_zone_selection()
                    zone_processed = True
                    continue
                elif reentry_result == "success_after_battle":
                    # 战斗后无再次入场：返回大厅→重新进入区域→检查扫荡
                    logging.info({"zh_CN": f"{zone_info['name']['zh_CN']}区域战斗后无再次入场，执行扫荡逻辑",
                                 "en_US": f"{zone_info['name']['en_US']} zone no re-entry after battle, execute sweep logic"})
                    self.back_to_zone_selection()
                    sleep(1)
                    # 重新进入当前区域
                    if not self.enter_grand_assault_zone(zone_info['name']['zh_CN'], zone_info["pos"]):
                        logging.error({"zh_CN": f"战斗后重新进入{zone_info['name']['zh_CN']}区域失败，跳过",
                                      "en_US": f"Failed to re-enter {zone_info['name']['en_US']} zone after battle, skip"})
                        zone_processed = True
                        continue
                    # 执行扫荡检查
                    raid_result = self.check_and_raid_quest(target_level)
                    # 扫荡成功，完成当前区域
                    if raid_result == "success":
                        zone_processed = True
                    # 无法扫荡，跳过当前区域
                    elif raid_result in ["no_raid_button", "no_ticket", "no_team"]:
                        logging.warn({"zh_CN": f"{zone_info['name']['zh_CN']}区域扫荡失败（{raid_result}），跳过",
                                     "en_US": f"{zone_info['name']['en_US']} zone sweep failed ({raid_result}), skip"})
                        zone_processed = True
                    # 扫荡后仍需战斗
                    elif raid_result == "need_battle":
                        logging.info({"zh_CN": f"{zone_info['name']['zh_CN']}区域扫荡后仍需战斗，重新处理",
                                     "en_US": f"{zone_info['name']['en_US']} zone still needs battle after sweep, reprocess"})
                elif reentry_result == "success":
                    # 首次检查无再次入场：直接执行扫荡
                    logging.info({"zh_CN": f"{zone_info['name']['zh_CN']}区域首次检查无再次入场，执行扫荡逻辑",
                                 "en_US": f"{zone_info['name']['en_US']} zone no re-entry on first check, execute sweep logic"})
                    raid_result = self.check_and_raid_quest(target_level)
                    # 扫荡成功，完成当前区域
                    if raid_result == "success":
                        zone_processed = True
                    # 无法扫荡，跳过当前区域
                    elif raid_result in ["no_raid_button", "no_ticket", "no_team"]:
                        logging.warn({"zh_CN": f"{zone_info['name']['zh_CN']}区域扫荡失败（{raid_result}），跳过",
                                     "en_US": f"{zone_info['name']['en_US']} zone sweep failed ({raid_result}), skip"})
                        zone_processed = True
                    # 需战斗，战斗后重新检查再次入场
                    elif raid_result == "need_battle":
                        logging.info({"zh_CN": f"{zone_info['name']['zh_CN']}区域扫荡需要战斗，返回重进",
                                     "en_US": f"{zone_info['name']['en_US']} zone sweep needs battle, return and re-enter"})
                
                # 返回区域选择主页面
                self.back_to_zone_selection()
                sleep(1)

        if has_entered_zone:
            config.append_noti_sentence(key="GRAND_ASSAULT_DATE", sentence=istr({
                CN: f"大决战开放中：{date_text}",
                EN: f"Grand assault open: {date_text}"
            }))
        else:
            config.append_noti_sentence(key="GRAND_ASSAULT_DATE", sentence=istr({
                CN: f"大决战未开放或结算中，下次开放日期或结算期限：{date_text}",
                EN: f"Grand assault not open or settlement in progress, next open date or settlement period: {date_text}"
            }))
        # 所有区域处理完成，领取奖励
        logging.info({"zh_CN": "所有区域处理完成，领取大决战奖励",
                     "en_US": "All zones processed, claim Grand Assault rewards"})
        CollectGrandAssaultReward().run()

    def post_condition(self) -> bool:
        return self.back_to_home()