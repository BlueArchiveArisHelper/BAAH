
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config
from modules.utils.log_utils import logging

class InContest(Task):
    def __init__(self, collect=True, name="InContest") -> None:
        super().__init__(name)
        # 是否领取奖励
        self.collect = collect

    def set_collect(self, collect :bool) -> None:
        self.collect = collect

    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)


    def on_run(self) -> None:
        if config.sessiondict["CONTEST_NO_TICKET"]:
            logging.info({"zh_CN": "上次进入竞技场已经无票卷，本次不再进入竞技场",
                          "en_US": "There are no tickets for the last time you entered the arena, "
                                   "you will not enter the arena this time"})
            self.back_to_home()
            return

        self.run_until(
            lambda: click((1196, 567)),
            lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            sleeptime=4
        )
        # 进入竞技场
        # 适配日服
        if config.userconfigdict["SERVER_TYPE"] == "JP" or config.userconfigdict["SERVER_TYPE"] == "GLOBAL":
            canincontest = self.run_until(
                lambda: click((878, 595)),
                lambda: Page.is_page(PageName.PAGE_CONTEST)
            )
        else:
            canincontest = self.run_until(
                lambda: click((1084, 550)),
                lambda: Page.is_page(PageName.PAGE_CONTEST)
            )
        if not canincontest:
            logging.warning({"zh_CN": "无法打开竞技场页面，跳过任务", "en_US": "Can't open contest page, task quit"})
            self.back_to_home()
            return
        # click the first enemy
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
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: not match(popup_pic(PopupName.POPUP_CONTEST_TARGET))
            )
        else:
            # Enter Editting Team Page
            # check whether jump option is open
            # if not, tick it
            # self.run_until(
            #     lambda: click((1144, 602)),
            #     lambda: match(button_pic(ButtonName.BUTTON_JUMP), returnpos=True)[2]>match(button_pic(ButtonName.BUTTON_NOT_JUMP), returnpos=True)[2]
            # )
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
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: not match(popup_pic(PopupName.POPUP_FIGHT_RESULT))
            )
        if self.collect:
            # receive the reward
            self.run_until(
                self.collect_and_magic,
                lambda: match(button_pic(ButtonName.BUTTON_CONTEST_COLLECT_BOTH_GRAY)),
                times=4
            )
        else:
            logging.info({"zh_CN": "设置的该次执行战术大赛不收集奖励, 直接返回主页",
                          "en_US": "The set execution tactical contest does not collect rewards, "
                                   "directly return to the homepage"})
        self.back_to_home()

    def collect_and_magic(self):
        click((352, 388))
        click((354, 467))
        sleep(1)
        click(Page.MAGICPOINT)

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)
