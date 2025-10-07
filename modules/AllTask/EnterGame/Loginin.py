import time

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils.log_utils import logging

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, check_app_running, open_app, config, screenshot, EmulatorBlockError, istr, CN, EN, match_pixel, OCR_LANG, ocr_area, get_screenshot_cv_data

from modules.AllTask.EnterGame.GameUpdate import GameUpdate

# =====

class Loginin(Task):
    def __init__(self, name="Loginin", pre_times = 3, post_times = 10) -> None:
        super().__init__(name, pre_times, post_times)
        # B站登录横幅，几个白色采样点
        self.BILI_LOGIN_BANNER_WHITE_POINTS = [[115, 20], [115, 73], [526, 76], [885, 18], [1093, 78], [1161, 22]]
        self.has_bili_login_banner = lambda: all([match_pixel(point, Page.COLOR_WHITE) for point in self.BILI_LOGIN_BANNER_WHITE_POINTS])
        # 如果在安装器页面的话，要识别并点击安装新版本按钮
        self.installer_activities = ["com.mumu.store", "com.android.packageinstaller"]
        self.installer_texts = ["更新", "安装", "启动", "打开"]
        # 识别关键字用于跳过一些弹窗，如Google框架提示，判断时会把ocr内容转小写
        self.click_keywords = [ 'google' ]
        # 检测是否已经登陆（出现Menu
        self.login_finish = False
     
    def pre_condition(self) -> bool:
        if(self.post_condition()):
            return False
        return True
    

    def try_jump_useless_pages(self):
        cv_data = get_screenshot_cv_data()
        height, width = cv_data.shape[0:2]
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
        # 已经登陆了，就近似恢复之前的逻辑，每隔一段时间点一下
        if self.login_finish:
            click((1250, 40))
        # 如果进入安装器页面
        elif any([check_app_running(ins_act) for ins_act in self.installer_activities]):
            # 中心区域识别所有安装字样点击
            ocr_list = ocr_area((312, 250), (967, 719), multi_lines=True, ocr_lang=OCR_LANG.ZHS)
            ocr_list = list(filter(lambda text: any([ins_text == text[0] for ins_text in self.installer_texts]), ocr_list))
            logging.info(ocr_list)
            if len(ocr_list) > 0:
                filter_item_box = ocr_list[0][2]
                click(((filter_item_box[0][0] + filter_item_box[1][0]) // 2, (filter_item_box[0][1] + filter_item_box[1][1]) // 2),
                    sleeptime=5)
        # 确认处在游戏界面
        elif not check_app_running(config.userconfigdict['ACTIVITY_PATH']):
            open_app(config.userconfigdict['ACTIVITY_PATH'])
            logging.warn({"zh_CN": "游戏未在前台，尝试打开游戏", "en_US":"The game is not in the foreground, try to open the game"})
            sleep(2)
            screenshot()

        # 大更新
        elif match(popup_pic(PopupName.POPUP_UPDATE_APP)):
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
        elif ocr_area((30, 662), (63, 691))[0].lower() in ["√", "v", "V"]:
            # 关闭活动弹窗
            # 判断点击左下角是否有今日不再显示的勾（√）并点掉
            click((65, 676))
        elif ocr_area([36, 626], [94, 652], ocr_lang = OCR_LANG.ZHS)[0].strip() == "菜单" or ocr_area([36, 626], [94, 652])[0].strip().lower() == "menu":
            # 第一次点击让游戏开始加载
            # 检测游戏加载前左下角的菜单字样
            click((1250, 40))
            self.login_finish = True
        elif any([click_word in ocr_area([300, 251], [900, 325])[0].strip().lower() for click_word in self.click_keywords]):
            # 识别到一些关键字弹窗后点击空白处关闭这个弹窗
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