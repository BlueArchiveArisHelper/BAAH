 

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils.log_utils import logging

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, check_app_running, open_app, config, screenshot

# =====

class Loginin(Task):
    def __init__(self, name="Loginin", pre_times = 3, post_times = 10) -> None:
        super().__init__(name, pre_times, post_times)

     
    def pre_condition(self) -> bool:
        if(self.post_condition()):
            return False
        return True
    

    @staticmethod
    def try_jump_useless_pages():
        # 确认处在游戏界面
        if not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
            open_app(config.userconfigdict['ACTIVITY_PATH'])
            logging.warn({"zh_CN": "游戏未在前台，尝试打开游戏", "en_US":"The game is not in the foreground, try to open the game"})
            sleep(2)
            screenshot()
        
        if match(button_pic(ButtonName.BUTTON_CONFIRMB)):
            # 点掉确认按钮
            click(button_pic(ButtonName.BUTTON_CONFIRMB))
        elif match(button_pic(ButtonName.BUTTON_USER_AGREEMENT)):
            # 用户协议
            click(button_pic(ButtonName.BUTTON_USER_AGREEMENT))
        elif match(button_pic(ButtonName.BUTTON_QUIT_LAST)):
            # 点掉放弃上次战斗进度按钮
            click(button_pic(ButtonName.BUTTON_QUIT_LAST))
        else:
            # 活动弹窗
            click((1250, 40))
    
     
    def on_run(self) -> None:
        # 因为涉及到签到页面什么的，所以这里点多次魔法点
        self.run_until(self.try_jump_useless_pages, 
                      lambda: match(popup_pic(PopupName.POPUP_LOGIN_FORM)) or Page.is_page(PageName.PAGE_HOME), 
                      times = 200,
                      sleeptime = 4)

     
    def post_condition(self) -> bool:
        return match(popup_pic(PopupName.POPUP_LOGIN_FORM)) or Page.is_page(PageName.PAGE_HOME)