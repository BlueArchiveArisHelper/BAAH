from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task
from modules.AllTask.AutoStory.SolveMain import SolveMain
from modules.AllTask.AutoStory.SolveShortOrSide import SolveShortOrSide

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)


class AutoStory(Task):
    """
        剧情自动化
        
        types = ["main", "short", "side"]

        main: 主线剧情

        short: 短篇剧情

        side: 支线剧情
    """

    def __init__(self, types, name="AutoStory") -> None:
        super().__init__(name)
        self.types = types

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def on_run(self) -> None:
        if "main-first" in self.types:
            SolveMain("main-first").run()
        if "main-second" in self.types:
            SolveMain("main-second").run()
        if "short" in self.types:
            SolveShortOrSide("short").run()
        if "side" in self.types:
            SolveShortOrSide("side").run()

    def post_condition(self) -> bool:
        return self.back_to_home()