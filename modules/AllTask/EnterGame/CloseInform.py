 

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, screenshot, config, _is_PC_app, _is_STEAM_app, get_correct_asset, AssetMappingKeys

class CloseInform(Task):
    def __init__(self, name="CloseInform", pre_times = 3, post_times = 3) -> None:
        super().__init__(name, pre_times, post_times)

     
    def pre_condition(self) -> bool:
        sleep(1)
        screenshot()
        if not match(popup_pic(PopupName.POPUP_LOGIN_FORM)) and not match(popup_pic(PopupName.POPUP_LOGIN_FORM_STEAM)):
            return False
        return True
    
     
    def on_run(self) -> None:
        click(Page.MAGICPOINT)

        close_login_shequ = get_correct_asset(config, AssetMappingKeys.CLOSE_LOGIN_SHEQU_POPUP)
        # STEAM 关闭社区弹窗
        click(close_login_shequ)

        click(Page.MAGICPOINT)

     
    def post_condition(self) -> bool:
        return self.back_to_home()