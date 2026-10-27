
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
from modules.AllTask.SubTask.RaidQuest import RaidQuest
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.ScrollSelect import SmartScrollSelect
import traceback

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP, is_server_type_in_group, MultiServerType, get_correct_asset, AssetMappingKeys
from modules.utils.log_utils import logging

class PushLevel(Task):
    """
    (可使用status) 把右侧关卡推关或刷取，如果是推关，level_list传入最后一关扫荡0次

    level_list: 关卡列表，里面是若干关卡下标和次数，如[[0, 20], [9, 10]]
    exploreORraid: 0表示推图，1表示扫荡
    storyORquest: 0表示剧情，1表示关卡
    """
    def __init__(self, level_list, exploreORraid = 0, storyORquest = 0, name="PushLevel") -> None:
        super().__init__(name)
        self.level_list = level_list
        self.exploreORraid = exploreORraid
        self.storyORquest = storyORquest
        self.story_button_xy = (766, 98)
        self.ocr_area = ((696, 149), (769, 683))
        # 如果有积分进度条，关卡窗口 endy 应该变为 589
        # 如果是quest，min_button_height 应该为60
        # 使用时记得深拷贝
        self.smart_scroll_params = {
            # targetind = level_ind,
            "window_starty":137,
            "window_endy":638,
            "clickx":1094,
            "active_button_color":Page.COLOR_BUTTON_BLUE,
            # 匹配task_info的图片并且对应区域是亮的就说明是可扫荡的
            "hasexpectimage": lambda: True,
            "swipeoffsetx":-100,
            "finalclick":True,
            "min_button_height":40,
            "ocr_area" : self.ocr_area
        }
        

     
    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_EVENT)

    def check_button_type_and_box(self):
        """检查当前页面的关卡区域高度和按钮高度，更改默认params"""
        if self.now_event_has_right_bottom_reward():
            self.smart_scroll_params["window_endy"] = 589
        if self.storyORquest == 1:
            self.smart_scroll_params["min_button_height"] = 60

    def now_event_has_right_bottom_reward(self):
        """检查当前活动的任务界面右下角是否有活动积分进度条以及按钮"""
        ocr_res = ocr_area([805, 650],[925, 675])[0].replace("/","").replace("|","")
        return ocr_res.isdecimal()

    def process_explore_mode_one_level(self,  level_ind):
        """处理推图模式"""
        goto_target_params = self.smart_scroll_params.copy()
        goto_target_params["targetind"] = level_ind
        goto_target_params["finalclick"] = False
        open_target_level = SmartScrollSelect(
            **goto_target_params
        )
        open_target_level.run()
        if open_target_level.status in [Task.STATUS_SUCCESS]:
            # 成功找到目标关卡，此时还未点击右侧按钮
            want_click_pos = open_target_level.wantclick_pos
            # 点击
            self.run_until(
                lambda: click(want_click_pos),
                lambda: self.has_popup(),
                times=3
            )
            # 检查是否已经通关最后一关（目标关卡）,由于这是靠ocr数字选取的关卡，不会选择到栏目底部奖励按钮
            already_passed = False
            if match(popup_pic(PopupName.POPUP_NOTICE)):
                # 如果匹配到通知，”通关故事/关卡x之后解锁“，则无需进行后续匹配，直接认为需要推图
                already_passed = False
            elif self.storyORquest == 0:
                # 故事模式检查 没有首次图标则判定已经通关
                if not match(button_pic(ButtonName.BUTTON_EVENT_FIRST), threshold=0.8):
                    already_passed = True
            elif self.storyORquest == 1:
                # 关卡模式检查 扫荡部分亮着则判定已经通关
                if self.has_popup() and (match(popup_pic(PopupName.POPUP_TASK_INFO)) or match(popup_pic(PopupName.POPUP_TASK_INFO_FANHEXIE))) and match_pixel([759, 353], [(120,120,120), (255,255,255)]):
                    already_passed = True
            if already_passed:
                logging.info(istr({
                    CN: f"已经通关最后一个关卡或剧情",
                    EN: f"Already passed the last level"
                }))
                self.status = self.STATUS_SUCCESS
                return
        # 需要推图
        logging.info(istr({
            CN: "需要推图",
            EN: "need to push level"
        }))
        self.clear_popup()
        # 推图逻辑为：滑动到倒数第一关（或者像素线上倒数第二关，有时候关卡奖励按钮也在那，所以需要识别左侧ocr数字），随后滑动到倒数第一关不断滚动打关
        # SmartScrollSelect通过-1下标找到目前打到哪一关了，默认下标0这关
        now_progress_ind = 0
        try:
            find_now_progress_params = self.smart_scroll_params.copy()
            find_now_progress_params["targetind"] = -1
            find_now_progress_params["finalclick"] = False
            find_now_progress_level = SmartScrollSelect(
                **find_now_progress_params
            )
            find_now_progress_level.run()
            if find_now_progress_level.status not in [Task.STATUS_SUCCESS]:
                logging.error(istr({
                    CN: "未能找到最后亮色按钮，结束",
                    EN: "Can not find the last light button, end"
                }))
                self.status = Task.STATUS_FAILED
                return
            # 得到欲点击位置，替换得到左侧ocr区域
            click_pos = find_now_progress_level.wantclick_pos
            logging.info(istr({
                CN: f"检测到最后一个亮色按钮：{click_pos}",
                EN: f"Detect the last blue button {click_pos}"
            }))
            y_center = click_pos[1] - 20
            x_center = 734
            half_block_length = 30
            ocr_one_level_area = ((x_center - half_block_length, y_center - half_block_length), 
                                  (x_center + half_block_length, y_center + half_block_length))
            logging.info(f"ocr area: {ocr_one_level_area}")
            ocr_res = ocr_area(ocr_one_level_area[0], ocr_one_level_area[1])[0].strip()
            if ocr_res.isdecimal(): # 判断由十进制数字组成
                now_progress_ind = int(ocr_res) - 1
                logging.info(istr({
                    CN: f"检测到最新待推关卡 {int(ocr_res)}",
                    EN: f"Detect new todo level {int(ocr_res)}"
                }))
            else:
                raise Exception(istr({
                    CN: f"未能ocr出已经推到的关卡数字 {ocr_res}",
                    EN: f"Did not find number result of ocr {ocr_res}"
                }))
            # 之后 now_progress_ind 就是目前推到哪一关的记录
            # 循环执行直到打完最后一关
            for _ in range(now_progress_ind, level_ind + 1):
                open_now_progress_popup = self.run_until(
                    lambda: click(click_pos),
                    lambda: self.has_popup(),
                    times = 3
                )
                if (not open_now_progress_popup) or (match(popup_pic(PopupName.POPUP_NOTICE))):
                    # 通知弹窗意味着上一关没能通过
                    logging.error(istr({
                        CN: f"未能打开期望的弹窗或中断关卡连续性，结束",
                        EN: f"Can not open desired popup or previous level broke, end"
                    }))
                    self.status = self.STATUS_FAILED
                    return
                # quest只需点 BUTTON_TASK_START, story 还需要考虑只有一个居中小弹窗的主要情况
                self.run_until(
                    lambda: click(button_pic(ButtonName.BUTTON_TASK_START)) or click((633, 496)),
                    lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE) or self.has_cost_popup(notice=False, diamond=False, price=True),
                    times=3,
                    sleeptime=2
                )
                if self.has_cost_popup(notice=False, diamond=False, price=True):
                    logging.error(istr({
                        CN: "体力不够，结束", 
                        EN: "Not enough AP, end"
                    }))
                    self.status = self.STATUS_SKIP
                    return
                # 单次战斗
                FightQuest(backtopic=lambda: match(page_pic(PageName.PAGE_EVENT)), auto_team = config.userconfigdict["ACTIVITY_AUTO_TEAM"]).run()
                # 战斗结束后，期望的now_progress_ind往后推一位,继续探测 click_pos
                now_progress_ind += 1
                find_now_progress_params = self.smart_scroll_params.copy()
                find_now_progress_params["targetind"] = now_progress_ind
                find_now_progress_params["finalclick"] = False
                find_now_progress_level = SmartScrollSelect(
                    **find_now_progress_params
                )
                find_now_progress_level.run()
                if find_now_progress_level.status not in [Task.STATUS_SUCCESS]:
                    logging.error(istr({
                        CN: f"未能找到下一个关卡 {now_progress_ind+1} 按钮，结束",
                        EN: f"Can not find the next level {now_progress_ind+1} button, end"
                    }))
                    self.status = Task.STATUS_FAILED
                    return
                click_pos = find_now_progress_level.wantclick_pos

        except Exception as e:
            logging.error(istr({
                CN: f"当执行推图探测的时候出现错误：{traceback.format_exc()}",
                EN: f"Error when detecting push level: {traceback.format_exc()}"
            }))
            self.status = self.STATUS_ERROR


    def process_raid_mode_one_level(self, level_ind, repeat_times):
        """处理扫荡模式"""
        # 参数模板
        raid_quest_params = self.smart_scroll_params.copy()
        raid_quest_params["targetind"] = level_ind
        raid_quest_params["hasexpectimage"] = lambda: self.has_popup() and (match(popup_pic(PopupName.POPUP_TASK_INFO)) or match(popup_pic(PopupName.POPUP_TASK_INFO_FANHEXIE))) and match_pixel([759, 353], [(120,120,120), (255,255,255)])
        # 实例化 SmartScrollSelect 并运行
        open_target_level = SmartScrollSelect(
            **raid_quest_params
        )
        open_target_level.run()
        if open_target_level.status in [Task.STATUS_SUCCESS]:
            logging.info(istr({
                CN: f"扫荡模式下，找到关卡{level_ind+1}对应的扫荡弹窗",
                EN: f"In sweep mode, the level {level_ind+1} can be found"
            }))
            RaidQuest(repeat_times).run()
        else:
            logging.error(istr({
                CN: f"扫荡模式下，找不到关卡{level_ind+1}对应的扫荡弹窗",
                EN: f"In sweep mode, the level {level_ind+1} cannot be found"
            }))
            self.status = self.STATUS_FAILED
     
    def on_run(self) -> None:
        self.check_button_type_and_box()
        # 按level执行
        for level in self.level_list:
            if self.exploreORraid == 1:
                # raid模式判断扫荡次数是否为0，为0则跳过
                if level[-1] == 'false' or level[-1] == False or level[-1] == 0 : # 开关关闭
                    logging.info(f"level {level[0]+1} swap times is 0 or not enabled, skip")
                    self.status = self.STATUS_SKIP
                    continue
            level_ind = level[0]
            repeat_times = level[1]
            # 推：剧情：翻到目标，如果能打开弹窗的话检查是不是有首次标签。如果打不开则从最后一个亮色按钮开始推；关卡：翻到目标，如果能打开弹窗的话检查是不是有扫荡按钮。如果打不开则从最后一个亮色按钮开始推。
            # 扫荡：关卡：翻到对应关卡开始判断能否扫荡。

            if self.exploreORraid == 0:
                # 推关模式
                self.process_explore_mode_one_level(level_ind)
            else:
                # 扫荡模式
                self.process_raid_mode_one_level(level_ind, repeat_times)
            # 每次for循环结束 clear_popup
            self.clear_popup()

     
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_EVENT)