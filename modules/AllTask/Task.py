from modules.AllPage.Page import Page
from DATA.assets.PageName import PageName
from DATA.assets.PopupName import PopupName
from DATA.assets.ButtonName import ButtonName


from modules.utils import click, swipe, match, page_pic, match_pixel, button_pic, popup_pic, sleep, screenshot, config, istr, CN, EN, ocr_area, logic_run_until, _is_steam_app

from modules.utils.adb_utils import check_app_running, open_app
from modules.utils.baah_exceptions import EmulatorBlockError
from modules.utils.log_utils import logging
import numpy as np

class Task:
    STATUS_SUCCESS = 0
    STATUS_ERROR = 1
    STATUS_SKIP = 2
    # 父类
    def __init__(self, name = "default Task", pre_times = 2, post_times = 4) -> None:
        self.name = name
        self.pre_times = pre_times
        self.post_times = post_times
        self.click_magic_when_run = True
        """运行时是否点击魔法点重置窗口状态到Page级别"""
        self.status = self.STATUS_SUCCESS
        
    def pre_condition(self) -> bool:
        """
        执行任务前的判断，判断现有情况，如果进行有效操作(截图或点击)，记得重新截图

        确认页面，是否需要做此任务，任务是否已经完成，这同时会试图点击魔法点重置页面状态到Page级别
        
        返回true表示可以执行任务，false表示不能执行任务
        """
        return True
        
    def on_run(self) -> None:
        """
        执行任务时需要做的事情，逻辑判断与操作
        
        如果是复杂的任务，尽量用run_until点击
        """
        pass
    
    def post_condition(self) -> bool:
        """
        执行任务后的判断，只判断现有情况，不要进行有效操作(截图或点击)

        看任务是否回到它该在的页面，这同时会试图点击魔法点重置页面状态到Page级别
        
        返回true表示回到它该在的页面成功，false表示回到它该在的页面失败
        """
        return True
    
    def run(self) -> None:
        """
        （不要重写）
        运行一个任务
        """
        logging.info({"zh_CN": "判断任务{}是否可以执行".format(self.name), "en_US":"Judge whether the task {} can be executed".format(self.name)})
        if(Task.run_until(self.click_magic_sleep,self.pre_condition, self.pre_times)):
            logging.info({"zh_CN": "执行任务{}".format(self.name), "en_US":"Run task {}".format(self.name)})
            self.on_run()
            logging.info({"zh_CN": "判断任务{}执行结果是否可控".format(self.name), "en_US":"Judge whether the task {} execution result is controllable".format(self.name)})
            if(Task.run_until(self.click_magic_sleep,self.post_condition, self.post_times)):
                logging.info({"zh_CN": "任务{}执行结束".format(self.name), "en_US":"Task {} execution completed".format(self.name)})
            else:
                logging.warn({"zh_CN": "任务{}执行后条件不成立或超时".format(self.name), "en_US":"The condition after the task {} is not met or timed out".format(self.name)})
                if not self.back_to_home():
                    raise Exception("任务{}执行后条件不成立或超时，且无法正确返回主页，程序退出".format(self.name))
        else:
            logging.warn({"zh_CN": "任务{}执行前条件不成立或超时，跳过此任务".format(self.name), "en_US":"The condition before the task {} is not met or timed out, skip this task".format(self.name)})
            config.append_noti_sentence(key = self.name+"_SKIP", sentence = istr({
                CN: f"跳过{self.name}任务",
                EN: f"Skip {self.name} task"
            }))

    @staticmethod
    def back_to_home(times = 3) -> bool:
        """
        尝试返回到游戏主页，如果游戏不在前台，会尝试打开游戏到前台，但不会等待登录加载，因此必须确保游戏在后台
        
        返回成功与否
        """
        logging.info({"zh_CN": "尝试返回主页", "en_US":"Try back to homepage"})
        can_back_home = False
        if not check_app_running(config.userconfigdict["ACTIVITY_PATH"]):
            open_app(config.userconfigdict["ACTIVITY_PATH"])
        for i in range(times):
            Task.clear_popup()
            # 有主页图标点击主页图标
            if match(button_pic(ButtonName.BUTTON_HOME_ICON)):
                click(button_pic(ButtonName.BUTTON_HOME_ICON), sleeptime=2.5)
                can_back_home = True
                Task.clear_popup()
            # 有社区弹窗，点关闭按钮
            if match(popup_pic(PopupName.POPUP_LOGIN_FORM)) or match(popup_pic(PopupName.POPUP_LOGIN_FORM_STEAM)):
                click(popup_pic(PopupName.POPUP_LOGIN_FORM), sleeptime=1) or click(popup_pic(PopupName.POPUP_LOGIN_FORM_STEAM), sleeptime=1)
                can_back_home = True
                Task.clear_popup()
            # 如果已经在主页
            if(Page.is_page(PageName.PAGE_HOME)):
                logging.info({"zh_CN": "返回主页成功", "en_US":"Successfully returned to the home page"})
                return True
            # 跳过故事
            screenshot()
            if match(button_pic(ButtonName.BUTTON_STORY_MENU)):
                menures = match(button_pic(ButtonName.BUTTON_STORY_MENU), returnpos=True)
                menuxy = menures[1]
                click(menuxy, sleeptime=1)
                click((menuxy[0], menuxy[1] + 80), sleeptime=1)
                screenshot()
                click(button_pic(ButtonName.BUTTON_CONFIRMB), sleeptime=3)
                can_back_home = True
            if can_back_home:
                sleep(3)
        logging.error({"zh_CN": "返回主页失败", "en_US":"Failed to return to home page"})
        return False
        
    
    @staticmethod
    def close_any_select_popup(yn: bool = False) -> bool:
        """
        关闭任一有选择性按钮的弹窗（确认弹窗，是否弹窗）一次

        yorn: boolean
            True: 关闭所有弹窗, 遇到选择选是
            False: 关闭所有弹窗, 遇到选择选否
        
        返回是否产生了关闭动作
        """
        # ...
        pass

    def click_magic_sleep(self, sleeptime = 3):
        if self.click_magic_when_run:
            click(Page.MAGICPOINT, sleeptime)
        else:
            sleep(sleeptime)

    @staticmethod
    def run_until(func1, func2, times=None, sleeptime = None) -> bool:
        return logic_run_until(func1, func2, times, sleeptime)

    @staticmethod
    def scroll_right_up(scrollx=928, times=3):
        """
        scroll to top
        """
        for i in range(times):
            swipe((scrollx, 226), (scrollx, 561), sleeptime=0.2)
        sleep(0.5)
    
    @staticmethod
    def scroll_right_down(times=3):
        """
        scroll to bottom
        """
        for i in range(times):
            swipe((928, 561), (928, 226), sleeptime=0.2)
        sleep(0.5)
        
    @staticmethod
    def scroll_left_up(times=3):
        """
        scroll to top
        """
        for i in range(times):
            swipe((265, 254), (264, 558), sleeptime=0.2)
        sleep(0.5)
    
    @staticmethod
    def scroll_left_down(times=3):
        """
        scroll to bottom
        """
        for i in range(times):
            swipe((264, 558), (265, 254), sleeptime=0.2)
        sleep(0.5)
    
    @staticmethod
    def scroll_to_left(times=3):
        """
        scroll to left
        """
        for i in range(times):
            swipe((459, 375), (797, 375), sleeptime=0.2)
        sleep(0.5)
    
    @staticmethod
    def scroll_to_right(times=3):
        """
        scroll to right
        """
        for i in range(times):
            swipe((797, 375), (459, 375), sleeptime=0.2)
        sleep(0.5)
        
    @staticmethod
    def clear_popup():
        """
        清除弹窗
        """
        def _close():
            if _is_steam_app(config.userconfigdict["SERVER_TYPE"]) and match(popup_pic(PopupName.POPUP_LOGIN_FORM_STEAM)):
                # 如果是STEAM且识别到社区弹窗，STEAM 关闭社区弹窗
                click((1123, 114))
            else:
                click(Page.MAGICPOINT)
        res = Task.run_until(
            lambda: _close(),
            lambda: not Task.has_popup(),
            times=15,
            sleeptime=0.5
        )
        if not res:
            logging.info("Popup clear failed")
        
    
    @staticmethod
    def has_popup():
        """
        判断是否有弹窗
        """
        if Page.is_page(PageName.PAGE_HOME):
            return not match_pixel((1027, 49), Page.COLOR_WHITE)
        return not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
    
    @staticmethod
    def has_cost_popup(notice = True, diamond = True, price = True):
        """
        判断是否有消费类弹窗，例如消耗钻石，金币，等

        传入参数代表是否检测对应类型的弹窗
        """
        if not Task.has_popup():
            # 没有弹窗
            return False
        if notice and match(popup_pic(PopupName.POPUP_NOTICE)):
            return True
        if diamond and match(popup_pic(PopupName.POPUP_USE_DIAMOND)):
            return True
        if price and match(popup_pic(PopupName.POPUP_TOTAL_PRICE), threshold=0.9):
            return True
        return False
    
    @staticmethod
    def _modify_now_teams_students(clear_all = False, auto_team = False):
        """取消当前选择队伍的所有人员 或者 进行自动编队"""
        # 快速编辑弹窗Empty人员的背景颜色
        COLOR_NO_STU_SELECTED = ([164, 158, 145], [184, 178, 174])
        # 自动编队按钮
        AUTO_TEAM_BUILD_BUTTON = [624, 593]
        # 快速编辑
        open_quick_edit_popup = Task.run_until(
            lambda: click([1202, 181]),
            lambda: Task.has_popup(),
            times=4
        )
        if not open_quick_edit_popup:
            logging.error(istr({
                CN: "打开快速编辑弹窗失败",
                EN: "Failed to open quick edit popup"
            }))
            return
        y_height = 572
        x_heights = np.linspace(76, 532, num=6, dtype=int)
        if clear_all:
            dont_care = True
            # 如果本来就是全空，不管了
            for x_height in x_heights:
                if not match_pixel((x_height, y_height), COLOR_NO_STU_SELECTED):
                    dont_care = False
                    break
            if not dont_care:
                # 全点一遍
                for x_height in x_heights:
                    click((x_height, y_height), sleeptime=0.2)
                # 检查一遍
                for x_height in x_heights:
                    Task.run_until(
                        lambda: click((x_height, y_height)),
                        lambda: match_pixel((x_height, y_height), COLOR_NO_STU_SELECTED),
                        times = 2
                    )
            logging.info(istr({
                CN: "清空所有人员",
                EN: "Clear All Students"
            }))
        elif auto_team:
            click(AUTO_TEAM_BUILD_BUTTON)
            click(AUTO_TEAM_BUILD_BUTTON)
        # 确认 关闭弹窗
        Task.run_until(
            lambda: click([1166, 570]),
            lambda: not Task.has_popup()
        )
    
    @staticmethod
    def set_auto_team(clear_team_inds = None, auto_team_inds = None):
        """
        进行自动编队，会先把不需要的队伍清空，然后把需要的队伍进行自动编队

        clear_team_inds: list
            需要清空的队伍下标，从0开始。默认清空1，2，3队伍
        
        auto_team_inds: list
            需要自动编队的队伍下标，从0开始。默认自动编队0队伍
        
        """
        if clear_team_inds is None:
            clear_team_inds = [i for i in range(1, 4)]
        if auto_team_inds is None:
            auto_team_inds = [0]
        logging.info(istr({
            CN: f"清空队伍index {clear_team_inds}，自动编队队伍index {auto_team_inds}",
            EN: f"Clear team index {clear_team_inds}, auto group team index {auto_team_inds}"
        }))
        # 取消所有队伍的在编人员
        for i in clear_team_inds:
            logging.info(istr({
                CN: f"清空队伍{i+1}",
                EN: f"Clear team {i+1}"
            }))
            Task.run_until(
                lambda: click(Page.LEFT_FOUR_TEAMS_POSITIONS[i]),
                lambda: not match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[i], Page.COLOR_WHITE)
            )
            Task._modify_now_teams_students(clear_all=True)
        # 然后选择队伍自动编队
        for i in auto_team_inds:
            logging.info(istr({
                CN: f"自动编队队伍 {i+1}",
                EN: f"Auto group team {i+1}"
            }))
            Task.run_until(
                lambda: click(Page.LEFT_FOUR_TEAMS_POSITIONS[i]),
                lambda: not match_pixel(Page.LEFT_FOUR_TEAMS_POSITIONS[i], Page.COLOR_WHITE)
            )
            Task._modify_now_teams_students(auto_team=True)