import time

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils.log_utils import logging

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, check_app_running, open_app, config, screenshot, EmulatorBlockError, istr, CN, EN, match_pixel

from modules.AllTask.EnterGame.GameUpdate import GameUpdate

# =====

class Loginin(Task):
    def __init__(self, name="Loginin", pre_times = 3, post_times = 10) -> None:
        super().__init__(name, pre_times, post_times)
        # B站登录横幅，几个白色采样点
        self.BILI_LOGIN_BANNER_WHITE_POINTS = [[115, 20], [115, 73], [526, 76], [885, 18], [1093, 78], [1161, 22]]
        self.has_bili_login_banner = lambda: all([match_pixel(point, Page.COLOR_WHITE) for point in self.BILI_LOGIN_BANNER_WHITE_POINTS])

     
    def pre_condition(self) -> bool:
        if(self.post_condition()):
            return False
        return True
    

    def try_jump_useless_pages(self):
        # 判断超时
        if time.time() - self.task_start_time > config.userconfigdict["GAME_LOGIN_TIMEOUT"]:
            if config.sessiondict["RESTART_EMULATOR_TIMES"] >= config.userconfigdict["MAX_RESTART_EMULATOR_TIMES"]:
                # 无重启次数剩余
                raise Exception(istr({
                    CN: "超时：无法进入游戏主页，无剩余重启次数",
                    EN: "Timeout: Fail to login to the game homepage, no restart chances left"
                }))
            else:
                # 有重启次数剩余，尝试重启
                raise EmulatorBlockError(istr({
                    CN: "模拟器卡顿，重启模拟器",
                    EN: "Emulator blocked, try to restart emulator"
                }))
        # 确认处在游戏界面
        if not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
            open_app(config.userconfigdict['ACTIVITY_PATH'])
            logging.warn({"zh_CN": "游戏未在前台，尝试打开游戏", "en_US":"The game is not in the foreground, try to open the game"})
            sleep(2)
            screenshot()

            # 大更新
        if match(popup_pic(PopupName.POPUP_UPDATE_APP)):
            if config.userconfigdict["BIG_UPDATE"]:
                GameUpdate().run()
                raise EmulatorBlockError(istr({
                    CN: "游戏进行了包体更新，触发了大更新流程，开始重新运行任务",
                    EN: "The game has performed a package update, triggering the big update process, starting to rerun the task"
                }))
            else:
                raise Exception(istr({
                    CN: "检测到新版本，未开启游戏包体更新，请手动更新",
                    EN: "New version detected, auto update is not enabled, please update manually"
                }))
        elif match(button_pic(ButtonName.BUTTON_CONFIRMB)):
            # 点掉确认按钮
            click(button_pic(ButtonName.BUTTON_CONFIRMB))
        elif match(button_pic(ButtonName.BUTTON_USER_AGREEMENT)):
            # 用户协议
            click(button_pic(ButtonName.BUTTON_USER_AGREEMENT))
        elif match(button_pic(ButtonName.BUTTON_QUIT_LAST)):
            # 点掉放弃上次战斗进度按钮
            click(button_pic(ButtonName.BUTTON_QUIT_LAST))
        elif match(button_pic(ButtonName.BUTTON_LOGIN_BILI)) and config.userconfigdict["SERVER_TYPE"] == "CN_BILI":
            # 点掉B站登录按钮
            # 防止点到上方横幅右侧切换账号按钮，这里睡4s等待横幅消失
            click(button_pic(ButtonName.BUTTON_LOGIN_BILI), sleeptime=4)
        elif self.has_bili_login_banner() and config.userconfigdict["SERVER_TYPE"] == "CN_BILI":
            # 如果出现B站登录横幅，睡2s等待横幅消失
            logging.info(istr({
                CN: "等待B站登录横幅消失",
                EN: "Waiting for the Bilibili login banner to disappear"
            }))
            sleep(2)
        else:
            # 活动弹窗
            click((1250, 40))
     
    def on_run(self) -> None:
        self.task_start_time = time.time()
        # 因为涉及到签到页面什么的，所以这里点多次魔法点
        self.run_until(self.try_jump_useless_pages, 
                      lambda: match(popup_pic(PopupName.POPUP_LOGIN_FORM)) or Page.is_page(PageName.PAGE_HOME), 
                      times = 200,
                      sleeptime = 4)

     
    def post_condition(self) -> bool:
        return match(popup_pic(PopupName.POPUP_LOGIN_FORM)) or Page.is_page(PageName.PAGE_HOME)