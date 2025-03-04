from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InCafe.InviteStudent import InviteStudent
from modules.AllTask.Task import Task
from modules.utils.log_utils import logging
from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config, match_pixel

# =====

from .CollectPower import CollectPower
from .TouchHead import TouchHead


class InCafe(Task):
    def __init__(self, name="InCafe", pre_times = 3, post_times = 3) -> None:
        super().__init__(name, pre_times, post_times)
        self.collect = config.userconfigdict["CAFE_COLLECT"]
        self.touch = config.userconfigdict["CAFE_TOUCH"]
        self.invite = config.userconfigdict["CAFE_INVITE"]
        self.invite1 = config.userconfigdict["CAFE_INVITE1"]
        self.invite2 = config.userconfigdict["CAFE_INVITE2"]

    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)

    def on_run(self) -> None:
        # 进入咖啡厅
        self.run_until(
            # 恰好是主页中的咖啡厅按钮，而又不是咖啡厅里的编辑按钮
            lambda: click((116, 687)) and click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_CAFE),
        )
        # 清除"今天到场的学生"弹窗
        if match(popup_pic(PopupName.POPUP_CAFE_VISITED)):
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: not match(popup_pic(PopupName.POPUP_CAFE_VISITED)),
            )
        if self.collect:
            # 收集体力
            CollectPower().run()
        else:
            logging.info({"zh_CN": "设置的咖啡馆不收集体力", "en_US": "set the config, do not gather energy"})
        inviteIndex = 0
        if self.touch:
            # 摸第一个咖啡厅头
            TouchHead().run()
            if self.invite1:
                config.sessiondict["CAFE_HAD_INVITED"] = False
                InviteStudent(inviteIndex).run()
                inviteIndex = inviteIndex + 1
                if config.sessiondict["CAFE_HAD_INVITED"]:
                    TouchHead(try_touch_epoch=1).run()
                else:
                    logging.warn({"zh_CN": "邀请学生失败，跳过第二次摸头",
                                  "en_US": "Failed to invite student, skip the second touch head"})
            else:
                logging.info({"zh_CN": "设置的咖啡馆1不邀请学生，跳过第二次摸头",
                              "en_US": "the setup file sets don't invite student, skip the second touch head"})
        else:
            logging.info({"zh_CN": "设置的咖啡馆1不摸头",
                          "en_US": "The setup file sets the cafe without touching the head"})
        # 清除弹窗
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
        )
        # 检测是否有第二个咖啡厅
        if match(button_pic(ButtonName.BUTTON_CAFE_SET_ROOM)):
            # 进入第二个咖啡厅
            logging.info({"zh_CN": "进入第二个咖啡厅", "en_US": "Entering the second cafe"})
            click(button_pic(ButtonName.BUTTON_CAFE_SET_ROOM), sleeptime=1)
            click((247, 165))
            if self.touch:
                # 摸第二个咖啡厅头
                TouchHead().run()
                if self.invite2:
                    config.sessiondict["CAFE_HAD_INVITED"] = False
                    InviteStudent(inviteIndex).run()
                    inviteIndex = inviteIndex + 1
                    if config.sessiondict["CAFE_HAD_INVITED"]:
                        TouchHead(try_touch_epoch=1).run()
                    else:
                        logging.info({"zh_CN": "设置的咖啡馆2不邀请学生，跳过第二次摸头",
                                      "en_US": "the config file set don't invite student, skip the second touch head"})
                else:
                    logging.info({"zh_CN": "设置的咖啡馆2不邀请学生，跳过第二次摸头",
                                  "en_US": "The set up cafe does not invite students, skipping the second touch"})
            else:
                logging.info({"zh_CN": "设置的咖啡馆2不摸头", "en_US": "Set cafe without touching the head"})
        # 返回主页
        Task.back_to_home()

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)