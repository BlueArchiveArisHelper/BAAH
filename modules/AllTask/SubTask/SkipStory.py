from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot


class SkipStory(Task):
    """
    前置条件为存在右上角Menu按钮

    点击跳过那个弹窗里的蓝色按钮并识别不到蓝色确认按钮后结束
    """

    def __init__(self, pre_times=10, name="SkipStory") -> None:
        # 前置判断时间弄久一点
        super().__init__(name, pre_times=pre_times)

    def pre_condition(self) -> bool:
        # 这里不能点击MAGICPOINT，因为有可能关闭momotalk弹窗
        return match(button_pic(ButtonName.BUTTON_STORY_MENU))

    def on_run(self) -> None:
        # 识别成功后记住按钮位置，下次尝试如果匹配不到MENU，直接点一下上次记的按钮位置
        self.last_recg_menupos = None
        for i in range(7):
            screenshot()
            # 记住MENU的位置
            menures = match(button_pic(ButtonName.BUTTON_STORY_MENU), returnpos=True)
            if not menures[0]:
                logging.info({"zh_CN": "跳过剧情被打断，重试", "en_US": "Skip the plot was interruption, try again"})
                if self.last_recg_menupos is not None:
                    click(self.last_recg_menupos)
                click(Page.MAGICPOINT, sleeptime=1.5)
                continue
            menupos = menures[1]
            self.last_recg_menupos = menupos
            # 按MENU,点击跳过直到看到蓝色确认按钮，这里MENU和跳过图标之间响应很快，直接连点
            clickmenu_and_skip = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_STORY_MENU), sleeptime=0.3) and click((menupos[0], menupos[1] + 80), sleeptime=1),
                lambda: match(button_pic(ButtonName.BUTTON_CONFIRMB))
            )
            if not clickmenu_and_skip:
                logging.info({"zh_CN": "跳过剧情被打断，重试", "en_US": "Skip the plot was interruption, try again"})
                continue
            # 点击蓝色确认按钮，直到看不到蓝色确认按钮
            clickconfirmb = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB), sleeptime=1),
                lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB)),
                times=3
            )
            if clickmenu_and_skip and clickconfirmb:
                logging.info({"zh_CN": "跳过剧情成功", "en_US": "skip the plot success"})
                # # 有时候跳过剧情后会有cg，这时候需要点击一下屏幕，看是不是有通知
                # click(Page.MAGICPOINT, sleeptime=1)
                # screenshot()
                # if match(popup_pic(PopupName.POPUP_NOTICE)):
                #     self.run_until(
                #         lambda: click(button_pic(ButtonName.BUTTON_CONFIRMB)),
                #         lambda: not match(button_pic(ButtonName.BUTTON_CONFIRMB)),
                #         times = 3
                #     )
                return
            else:
                logging.info({"zh_CN": "跳过剧情被打断，重试", "en_US": "Skip the plot was interruption, try again"})
        raise Exception("跳过剧情失败，可能是剧情按钮的图片变化了，请反馈")

    def post_condition(self) -> bool:
        return not match(button_pic(ButtonName.BUTTON_CONFIRMB))