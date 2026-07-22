
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging


def from_inner_page_safe_back_to_event_page():
    """
    从抽奖等子页面安全返回活动页面，避免在抽奖页面中出现异常导致无法返回活动页面
    """
    Task.clear_popup()
    return Task.run_until(
        lambda: click(Page.TOPLEFTBACK),
        lambda: Page.is_page(PageName.PAGE_EVENT),
        sleeptime = 2,
        times = 3
    )