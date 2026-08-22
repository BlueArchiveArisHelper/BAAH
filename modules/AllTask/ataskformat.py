
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP, is_server_type_in_group, MultiServerType, get_correct_asset, AssetMappingKeys
from modules.utils.log_utils import logging

class NameOfTask(Task):
    def __init__(self, name="NameOfTask") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return super().pre_condition()
    
     
    def on_run(self) -> None:
        super().on_run()

     
    def post_condition(self) -> bool:
        return super().post_condition()