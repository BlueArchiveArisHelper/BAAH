from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.GridQuest import GridQuest

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)
from modules.utils.grid_analyze import GridAnalyzer
from .Questhelper import (jump_to_page, close_popup_until_see, judge_whether_3star, quest_has_easy_tab, easy_tab_pos_R, center_tab_pos_L)


class PushQuest(Task):
    """
    从进入关卡选择页面开始托管推图

    通过page_ind和level_ind定位到起始关卡，随后每成功推一张图就让level_ind+1，向右多翻一次后，用ocr来更新确切的page_ind和level_ind

    Parameters
    ----------
    quest_type : str
        任务类型，normal/hard

    page_ind : int
        开始推图的章节下标
    """

    def __init__(self, quest_type, page_ind, level_ind=0, name="PushQuest") -> None:
        super().__init__(name)
        self.is_normal = quest_type == "normal"
        self.page_ind = page_ind  # 初始聚焦章节下标
        self.level_ind = level_ind  # 初始聚焦关卡下标
        self.require_type_ind = 0  # 当前需要完成的任务类型下标
        self.start_from_level_popup = False # 此属性为True时，直接从挑战任务那跳转到的关卡弹窗页面开始本任务
        self.challenge_only = False # 是否是为了挑战任务，此属性为True时，一关打完后不会往后推

    def pre_condition(self) -> bool:
        if self.start_from_level_popup:
            return True
        return Page.is_page(PageName.PAGE_QUEST_SEL)

    def on_run(self) -> None:
        if not self.start_from_level_popup:
            if self.is_normal:
                logging.info({"zh_CN": "切换到普通关卡", "en_US": "switch to normal quest"})
                self.run_until(
                    lambda: click((798, 159)),
                    lambda: match(button_pic(ButtonName.BUTTON_NORMAL))
                )
            else:
                logging.info({"zh_CN": "切换到困难任务", "en_US": "switch to hard quest"})
                self.run_until(
                    lambda: click((1064, 161)),
                    lambda: match(button_pic(ButtonName.BUTTON_HARD))
                )
        while 1:
            if not self.start_from_level_popup:
                # ===========尝试定位要推图的章节和关卡===================
                # 跳转到相应地区
                logging.info({"zh_CN": "尝试跳转至页面 {}".format(self.page_ind + 1),
                            "en_US": "Try jumping to page {}".format(self.page_ind + 1)})
                jumpres = jump_to_page(self.page_ind + 1)  # 下标加1为实际页号数字
                if not jumpres:
                    logging.error({"zh_CN": "跳转至页面 {} 失败，结束此任务".format(self.page_ind + 1),
                                "en_US": "Cannot jump to page {}, end this task".format(self.page_ind + 1)})
                    return
                click(Page.MAGICPOINT, sleeptime=1)
                self.scroll_right_up()
                sleep(3)
                # 清除弹窗
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
                )
                # 点击第一个关卡
                self.run_until(
                    lambda: click((1118, 240)),
                    lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
                )
                # 此时应该看到扫荡弹窗
                # 判断是否有简易攻略tab

                # 向右翻self.level_ind次
                logging.info({"zh_CN": "尝试翻到关卡 {}".format(self.level_ind + 1),
                            "en_US": "Try flipping to level {}".format(self.level_ind + 1)})
                for i in range(self.level_ind):
                    click((1171, 359), sleeptime=1)
                screenshot()
                # 如果匹配到弹窗消失
                if match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE):
                    logging.info({"zh_CN": "关卡弹窗消失，结束此任务","en_US": "Level popup disappears, end this task"})
                    return
            # 重置start_from_level_popup（只有第一次进入while时需要进行判断start_from_level_popup）
            self.start_from_level_popup = False
            # 此时判断是否有简易攻略tab
            has_easy_tab = quest_has_easy_tab()
            # 当前关卡就是这次需要推图的关卡
            offsetx = 0
            # 往下偏移了30，由于简易攻略tab
            offsety = 0
            if has_easy_tab:
                logging.info({"zh_CN": "存在简易攻略", "en_US": "There is a short guide"})
                offsety = 30
            # 识别关卡序号，更新最新的page_ind和level_ind
            left_up = ocr_area((139 + offsetx, 197 + offsety), (225 + offsetx, 232 + offsety))
            page_level = left_up[0].split(" ")[0].replace("|", "").replace("[", "").replace("I", "").replace("]", "").strip().split("-")
            # 后处理split("-")后面的内容，ocr容易把关卡分隔符识别成1，这里判断如果关卡号两位数,只保留两位数的第一位
            if len(page_level) == 2 and len(page_level[1]) == 2:
                page_level[1] = page_level[1][0]
            try:
                # 如16-4这种数字组合都能够成功分割
                logging.info({"zh_CN": f"分割后的关卡序号：{page_level}",
                              "en_US": f"Split Level Sequence: {page_level}"})
                assert len(page_level)==2
                # 这一步更新这次推图的实际章节和关卡下标
                page_num = int(page_level[0])
                self.page_ind = page_num - 1
                if page_level[1] == "A" or page_level[1] == "B" or page_level[1] == "C":
                    # 如果为A/B/C关卡，就直接把来到这里的这一次的level作为这次的level
                    # 一般来说关卡号为A的关卡都是一章节的最后一关，且为普通关，打完后不会消失
                    # 最后self.level_ind+1，前往下一关
                    logging.info({"zh_CN": "战斗关卡 {}-{}，开始推图".format(page_num, page_level[1]),
                                  "en_US": "Battle level {} - {}, start thumbnail".format(page_num, page_level[1])})
                else:
                    level_num = int(page_level[1])
                    # 否则将识别到的关卡序号-1作为这次的level下标
                    self.level_ind = level_num - 1
                    logging.info({"zh_CN": "格子关卡：{}-{}，开始推图".format(page_num, level_num),
                                  "en_US": "Grid level: {} - {}, start thumbnail".format(page_num, level_num)})
            except:
                # 如果遇到支线关，分割失败；有时候24-A这种偶尔也会分割失败，
                logging.warn({"zh_CN": f"OCR关卡序号识别失败({left_up[0]})",
                              "en_US": f"Failing to recognize the level number({left_up[0]})"})
                if not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE):
                    if self.level_ind == 5 and ("A" in left_up[0] or "B" in left_up[0] or "C" in left_up[0]):
                        # 如果 关卡下标为 五并且匹配到数字A,B,C，说明是章节末尾关卡，打完后不会消失
                        logging.info({"zh_CN": "判断为章节末尾关卡",
                                      "en_US": "Judged as a level at the end of the chapter"})
                    else:
                        # 如果没有匹配A,B,C，说明是支线关卡，打完就会消失
                        logging.info({"zh_CN": "判断为支线关卡", "en_US": "Judged as Side Stage"})
                        # 这里将level_ind-1，因为支线关卡打完后会消失，后面的关相当于自动往前进一格，让后面打完后的level_ind+1刚好抵消
                        self.level_ind -= 1
                else:
                    logging.error({"zh_CN": f"OCR关卡序号识别失败({left_up[0]}), 且未匹配到开始任务弹窗，结束此任务",
                                   "en_US": f"Cannnot recognize the level number({left_up[0]}), "
                                            f"and not match the start task popup, end this task"})
                    return
            # ===========正式开始推图===================
            # 看到弹窗，ocr是否有S
            ocr_s = ocr_area((327 + offsetx, 257 + offsety), (370 + offsetx, 288 + offsety))
            # 如果有简易攻略tab，有简易攻略tab存在，这个图肯定默认是格子图
            if has_easy_tab:
                if (self.is_normal and config.userconfigdict["PUSH_NORMAL_USE_SIMPLE"]) or (not self.is_normal and config.userconfigdict["PUSH_HARD_USE_SIMPLE"]):
                    logging.info({"zh_CN": "使用简易攻略", "en_US": "Use simple explore"})
                    click(easy_tab_pos_R)
                    click(easy_tab_pos_R)
                    # 简易攻略的话，把ocr_s设为_，让后面不要走格子(no "S")
                    ocr_s = ["_", 1.0]
                else:
                    logging.info({"zh_CN": "不使用简易攻略",
                                  "en_US": "Do not use simple explore"})
                    click(center_tab_pos_L)
                    click(center_tab_pos_L)
                    # 切换到集中指挥tab后，才会出现s标签，没有必要再次识别
                    ocr_s = ["S", 1.0]


            walk_grid = None
            logging.info("OCR: "+ocr_s[0].upper())
            if "S" not in ocr_s[0].upper():
                logging.info({"zh_CN": "未识别到S等级，判断为普通战斗",
                              "en_US": "S grade not recognized, judged as normal battle"})
                walk_grid = False
            else:
                logging.info({"zh_CN": "识别到S标签，判断为走格子战斗",
                              "en_US": "Identified the S tag and judged it to be a grid fight"})
                walk_grid = True
            if not walk_grid:
                enteredit = self.run_until(
                    # 等级过高会有个 蓝色的确认按钮 警告等级过高的通知，直接点掉
                    lambda: click(button_pic(ButtonName.BUTTON_TASK_START)) or click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                    # 如果检测到蓝色OK，此lambda应当阻止进行has_cost_popup的检测
                    lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB)) and  (match(page_pic(PageName.PAGE_EDIT_QUEST_TEAM)) or self.has_cost_popup()) # 防止漏检测，此处cost_popup里检测到通知弹窗则认为是要买票
                    # 体力不足弹窗标题购买体力，卷票次数不足标题是“通知”
                )
                if self.has_cost_popup():
                    logging.info(istr({
                        CN: "检测到消费弹窗，退出",
                        EN: "Match cost popup, quit"
                    }))
                    self.status = self.STATUS_SKIP
                    self.clear_popup()
                    return
                # 识别不到大的开始任务按钮，可能是支线任务
                if not enteredit:
                    # 支线任务的开始任务按钮在中间，且比较小
                    click_middle_button = self.run_until(
                        lambda: click((639, 516)),
                        lambda: match(page_pic(PageName.PAGE_EDIT_QUEST_TEAM))
                    )
                FightQuest(
                    backtopic=lambda: match(page_pic(PageName.PAGE_QUEST_SEL)), 
                    auto_team=config.userconfigdict["EXPLORE_AUTO_TEAM"]
                ).run()
                # 普通任务完成后，level下标直接+1。如果是支线关卡，由于之前减过一了，这里直接+1就行
                self.level_ind += 1
            else:
                jsonname = f"{self.page_ind + 1}-{self.level_ind + 1}.json"
                if not self.is_normal:
                    jsonname = f"H{jsonname}"
                grider = GridAnalyzer("quest", jsonfilename=jsonname)
                click(button_pic(ButtonName.BUTTON_TASK_START), sleeptime=2)
                # 等级过高会有个 蓝色的确认按钮 警告等级过高的通知，直接点掉
                self.run_until(
                    lambda: click(button_pic(ButtonName.BUTTON_TASK_START)) or click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                    # 如果检测到蓝色OK，此lambda应当阻止进行has_cost_popup的检测
                    lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB)) and (match(page_pic(PageName.PAGE_GRID_FIGHT)) or self.has_cost_popup())
                    # 体力不足弹窗标题购买体力，卷票次数不足标题是“通知”
                )
                if self.has_cost_popup():
                    logging.info(istr({
                        CN: "检测到消费弹窗，退出",
                        EN: "Match cost popup, quit"
                    }))
                    self.status = self.STATUS_SKIP
                    self.clear_popup()
                    return
                # 需求列表
                require_types = list(grider.get_requires_list().keys())
                if self.challenge_only:
                    # 如果只是为了挑战任务
                    choose_types_ind = 0
                    shortest_steps = float("inf")
                    for ind in range(len(require_types)):
                        # 选取靠后且fight_plan较短的
                        type_name = require_types[ind]
                        type_steps = grider.get_num_of_steps(type_name)
                        if type_steps <= shortest_steps:
                            choose_types_ind = ind
                else:
                    choose_types_ind = self.require_type_ind
                GridQuest(grider=grider, 
                          backtopic=lambda: match(page_pic(PageName.PAGE_QUEST_SEL)),
                          require_type=require_types[choose_types_ind],
                          auto_team=config.userconfigdict["EXPLORE_AUTO_TEAM"]).run()
                # 判断是否只打当前关
                if self.challenge_only:
                    self.clear_popup()
                    return
                # 任务完成后，往后切换需求类型下标，如果超出了需求类型列表，就回到0，且level下标+1
                self.require_type_ind += 1
                if self.require_type_ind >= len(require_types):
                    self.require_type_ind = 0
                    self.level_ind += 1
            logging.info({"zh_CN": f"一个战斗完成，更新关卡下标为{self.level_ind}, 更新流程类型下标为{self.require_type_ind}",
                          "en_US": f"One battle completed, update level subscript to {self.level_ind}, update process type index to {self.require_type_ind}"})
            sleep(6) # 等待6秒：可能的新章节解锁动画

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_QUEST_SEL)