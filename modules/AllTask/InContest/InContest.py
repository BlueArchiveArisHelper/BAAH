
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config, filter_num, istr, CN, EN, ocr_area
from modules.utils.log_utils import logging

class InContest(Task):
    def __init__(self, collect=True, name="InContest") -> None:
        super().__init__(name)
        # 是否领取奖励
        self.collect = collect

    def set_collect(self, collect :bool) -> None:
        self.collect = collect

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def recognize_rank(self) -> list[int]:
        res_list = []
        res_list.append(filter_num(ocr_area((129, 288), (270, 339))[0]))
        other3_L_T_Y = [200, 360, 520]
        other3_X = 553
        other3_offset = (160, 50)
        
        for y in other3_L_T_Y:
            res_list.append(filter_num(ocr_area((other3_X, y), (other3_X+other3_offset[0], y+other3_offset[1]))[0]))
        
        return [int(each) for each in res_list]

    def recognize_level(self) -> list[int]:
        res_list = []
        res_list.append(filter_num(ocr_area((162, 186), (226, 213))[0]))
        other3_L_T_Y = [291, 449, 609]
        other3_X = 461
        other3_offset = (56, 26)

        for y in other3_L_T_Y:
            res_list.append(filter_num(ocr_area((other3_X, y), (other3_X+other3_offset[0], y+other3_offset[1]))[0]))
        
        return [int(each) for each in res_list]
        
    def collect_reward(self):
        self.run_until(
            self.click_collect_and_magic,
            lambda: match(button_pic(ButtonName.BUTTON_CONTEST_COLLECT_BOTH_GRAY)),
            times=4
        )

    def on_run(self) -> None:
        if config.sessiondict["CONTEST_NO_TICKET"]:
            logging.info({"zh_CN": "上次进入竞技场已经无票卷，本次不再进入竞技场",
                          "en_US": "There are no tickets for the last time you entered the arena, "
                                   "you will not enter the arena this time"})
            self.collect_reward()
            self.back_to_home()
            return

        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # 进入竞技场
        canincontest = self.run_until(
            lambda: click((878, 595)),
            lambda: Page.is_page(PageName.PAGE_CONTEST)
        )
        if not canincontest:
            logging.warning({"zh_CN": "无法打开竞技场页面，跳过任务", "en_US": "Can't open contest page, task quit"})
            self.back_to_home()
            return
        self.clear_popup()
        try: 
            rank_list = self.recognize_rank()
            level_list = self.recognize_level()
            assert len(rank_list) == len(level_list)
            # 计算加权
            pri_level = config.userconfigdict["CONTEST_LEVEL_PRIORITY"]
            pri_rank = config.userconfigdict["CONTEST_RANK_PRIORITY"]
            score_list = []
            for i in range(len(rank_list)):
                if i==0:
                    # 自己，不计算
                    continue
                else:
                    # 排名：自己的除以别人的
                    # 等级：自己的除以别人的
                    score_list.append(pri_rank*(rank_list[0]/rank_list[i]) + pri_level*(level_list[0]/level_list[i]))
            logging.info(f"score list: {score_list}")
            
            # 选取最大值
            max_score = max(score_list)
            max_index = score_list.index(max_score)
            # 点击对应的目标
            click_pos_list = [(994, eachy) for eachy in (230, 390, 550)]
            self.run_until(
                lambda: click(click_pos_list[max_index]),
                lambda: match(popup_pic(PopupName.POPUP_CONTEST_TARGET))
            )
            
        except Exception as e:
            logging.error(istr({
                CN: f"识别竞技场信息错误: {e}",
                EN: f"Error in identifying contest information: {e}"
            }))
            self.clear_popup()
            # 点击第一个目标
            self.run_until(
                lambda: click((994, 241)),
                lambda: match(popup_pic(PopupName.POPUP_CONTEST_TARGET))
            )
        # click the start button in the popup
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_EDIT)),
            lambda: Page.is_page(PageName.PAGE_EDIT_TEAM) or match(popup_pic(PopupName.POPUP_NOTICE)) or match(popup_pic(PopupName.POPUP_USE_DIAMOND))
        )
        #  匹配到通知弹窗或者匹配到使用钻石弹窗，说明没有票卷了，为什么日服的通知标题有时候是片假名有时候是汉字啊
        if match(popup_pic(PopupName.POPUP_NOTICE)) or match(popup_pic(PopupName.POPUP_USE_DIAMOND)):
            # if no ticket
            logging.warning({"zh_CN": "已经无票卷...尝试收集奖励", "en_US": "No ticket...try to collect reward"})
            # sessiondict设置
            config.sessiondict["CONTEST_NO_TICKET"] = True
            # 强制收集
            self.collect = True
            # close all popup
            self.clear_popup()
        else:
            # Enter Editting Team Page
            # check whether jump option is open
            # if not, tick it
            self.run_until(
                lambda: click((1144, 602)),
                lambda: match(button_pic(ButtonName.BUTTON_JUMP), returnpos=True)[2]>match(button_pic(ButtonName.BUTTON_NOT_JUMP), returnpos=True)[2]
            )
            # go fight and return to the Fight Result Popup
            # 点击战斗按钮，此时是一定有票的，但是有可能冷却还没过，所以要多次尝试，最大60s冷却
            # 这之间会不断弹出剩余时间弹窗，不过依旧能检测到战斗按钮，所以不影响
            sleep(2)
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_GOFIGHT)),
                lambda: match(popup_pic(PopupName.POPUP_FIGHT_RESULT)),
                times=20,
                sleeptime=2
            )
            # click magic point to close the Result popup, back to pure contest page
            self.clear_popup()
        if self.collect:
            # receive the reward
            self.collect_reward()
        else:
            logging.info({"zh_CN": "设置的该次执行战术大赛不收集奖励, 直接返回主页",
                          "en_US": "The set execution tactical contest does not collect rewards, "
                                   "directly return to the homepage"})
        self.back_to_home()

    def click_collect_and_magic(self):
        click((352, 388))
        click((354, 467))
        self.clear_popup()

    def post_condition(self) -> bool:
        return self.back_to_home()
