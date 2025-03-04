from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config, ocr_area, close_app
# =====
from .Loginin import Loginin
from .CloseInform import CloseInform

class EnterGame(Task):
    def __init__(self, name="EnterGame" , pre_times = 1, post_times = 10) -> None:
        super().__init__(name, pre_times, post_times)
    
    def record_resources(self):
        """
        记录主页中的资源
        """
        # 记录主页中的资源
        power_num = ocr_area((503, 17), (602, 56))[0]
        # print("体力: ", power_num)
        credit_num = ocr_area((688, 19), (832, 59))[0]
        # print("信用点: ", credit_num)
        diamond_num = ocr_area((863, 21), (973, 60))[0]
        # print("钻石: ", diamond_num)
        config.sessiondict["BEFORE_BAAH_SOURCES"] = {"power": power_num, "credit": credit_num, "diamond": diamond_num}
     
    def pre_condition(self) -> bool:
        if Page.is_page(PageName.PAGE_HOME):
            # 直接就在主页，直接记录资源
            self.record_resources()
            return False
        if match(button_pic(ButtonName.BUTTON_HOME_ICON)):
            return_home = self.back_to_home()
            if return_home:
                # 如果成功返回主页，记录资源
                self.record_resources()
            return not return_home
        return True
    
     
    def on_run(self) -> None:
        Loginin().run()
        close_app("com.android.browser")
        CloseInform().run()
        close_app("com.android.browser")
        # 如果登入到游戏，记录资源
        self.record_resources()
        
    
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)