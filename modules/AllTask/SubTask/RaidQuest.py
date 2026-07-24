from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import (click, ocr_area_0, swipe, match, page_pic, button_pic, popup_pic, sleep,
                           ocr_area, screenshot, config, match_pixel, istr, CN, EN)



class RaidQuest(Task):
    """
    从看到扫荡弹窗开始，到点击了扫荡按钮或购买按钮结束，默认不包含后续关闭收获弹窗/购买弹窗的操作。

    Parameters
    ==========
    raidtimes: int
        扫荡次数，-1为最大次数，-n为最大次数减去若干次，0为不扫荡，正数为具体扫荡次数
    recall_close：function
        回调函数，用于后续关闭弹窗，通常建议将关闭操作放在此class外部
    has_easy_tab: bool
        是否有简易攻略tab，用于适配简易攻略扫荡弹窗
    """

    def __init__(self, raidtimes, recall_close=None, has_easy_tab=False, name="RaidQuest") -> None:
        super().__init__(name)
        self.raidtimes = raidtimes
        self.click_magic_when_run = False
        self.has_easy_tab = has_easy_tab
        # 回调函数，用于关闭弹窗
        self.recall_close = recall_close

        self.max_pos = (1084, 299)
        self.add_pos = (1017, 300)
        self.minus_pos = (857, 301)
        self.ocr_area_pos_1 = (906, 284)
        self.ocr_area_pos_2 = (970, 318)
        if self.has_easy_tab:
            # 日服简易攻略扫荡弹窗位置需要往下偏移
            self.max_pos = (1084, 299 + 30)
            self.add_pos = (1017, 300 + 30)
            self.minus_pos = (857, 301 + 30)
            self.ocr_area_pos_1 = (906, 284 + 30)
            self.ocr_area_pos_2 = (970, 318 + 30)

    def pre_condition(self) -> bool:
        # 判断默认的次数不是0才能进入
        if ocr_area_0(self.ocr_area_pos_1, self.ocr_area_pos_2):
            logging.warn(istr({
                CN: "扫荡次数为0，无法扫荡",
                EN: "Raid number is 0, cannot raid"
            }))
            return False
        if not self.has_popup():
            logging.warn(istr({
                CN: "没有弹出扫荡弹窗，无法扫荡",
                EN: "Raid popup not found, cannot raid"
            }))
            return False
        return True

    def check_has_max(self) -> bool:
        """
        通过检查数字是否变化来判断是否可以通过max times来扫荡
        """
        screenshot()
        now_num = ocr_area(self.ocr_area_pos_1, self.ocr_area_pos_2)[0]
        # 点一下max
        click(self.max_pos)
        screenshot()
        next_num = ocr_area(self.ocr_area_pos_1, self.ocr_area_pos_2)[0]
        if now_num == next_num:
            return False
        return True

    def on_run(self) -> None:
        # 全局变量存储当前这次任务是否可继续扫荡的信息
        # 但不应当在开始就判断是否不合法，因为可能now_activate_pipeline里有多次同名任务
        # 判断是否提前中止的操作应当交给外部循环层考虑
        repeat_times = self.raidtimes
        # 弹出任务咨询页面后选择次数
        if repeat_times < 0:
            # 检测能够通过max times来扫荡
            if self.check_has_max():
                # max times
                click(self.max_pos)
            else:
                # 点加号多次然后长按
                click(self.add_pos, sleeptime=0.1)
                click(self.add_pos, sleeptime=0.1)
                swipe(self.add_pos, self.add_pos, durationtime=6)
            # max后反向减少次数
            if repeat_times < -1:
                # max times - Math.abs(repeat_times)
                # 按减号
                # decrease times
                for t in range(abs(repeat_times)):
                    click(self.minus_pos)
        elif repeat_times == 0:
            logging.info({"zh_CN": "扫荡次数为0，不扫荡", "en_US": "raid number is 0, don't raid"})
            return
        else:
            for t in range(max(0, repeat_times - 1)):
                # increase times
                click(self.add_pos)
        # 扫荡按钮点击后，有三个可能，一个是弹出确认提示，一个是弹出购买体力的提示，还有个是购买困难扫荡券的提示
        screenshot()

        # 考虑国服识别反和谐扫荡按钮
        if not (match(button_pic(ButtonName.BUTTON_CFIGHT_START)) or match(button_pic(ButtonName.BUTTON_CFIGHT_START_FANHEXIE))):
            logging.error({"zh_CN": "扫荡（快速战斗）按钮匹配失败，请检查配置文件中的服务器语言，以及是否有反和谐",
                          "en_US": "Failed to match raid button, please check the server language in config file"})

        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_CFIGHT_START)) or click(button_pic(ButtonName.BUTTON_CFIGHT_START_FANHEXIE)),
            lambda: match(popup_pic(PopupName.POPUP_NOTICE)) or
                        match(popup_pic(PopupName.POPUP_TOTAL_PRICE), threshold=0.9) or
                        match(popup_pic(PopupName.POPUP_USE_DIAMOND), threshold=0.85)
        )
        # 如果弹出购买体力/票卷的弹窗，取消任务
        if match(popup_pic(PopupName.POPUP_TOTAL_PRICE), threshold=0.9):
            logging.warn({"zh_CN": "检测到购买体力/卷票弹窗，取消此次扫荡任务",
                          "en_US": "Detected purchase AP/ticket popup, cancel this raid task"})
        elif match(popup_pic(PopupName.POPUP_USE_DIAMOND), threshold=0.85):
            # 困难关卡恢复挑战次数
            logging.warn({"zh_CN": "检测到需要消耗钻石，跳过关卡扫荡",
                          "en_US": "Detected need to consume diamond, skip raiding"})
        else:
            # 弹出确认框，点击确认
            logging.info({"zh_CN": "点击弹窗内的确认", "en_US": "Click Confirm in the pop-up"})
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                lambda: not match(popup_pic(PopupName.POPUP_NOTICE))
            )
        # 如果传入了回调函数，则调用它来关闭弹窗
        if self.recall_close:
            self.recall_close()

    def post_condition(self) -> bool:
        return True