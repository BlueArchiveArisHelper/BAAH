from modules.AllPage.Page import Page
from DATA.assets.PageName import PageName
from DATA.assets.PopupName import PopupName
from DATA.assets.ButtonName import ButtonName


from modules.utils import click, swipe, match, page_pic, match_pixel, button_pic, popup_pic, sleep, screenshot, config

from modules.utils.log_utils import logging


class Task:
    # 父类
    def __init__(self, name, pre_times = 2, post_times = 4) -> None:
        self.name = name
        self.pre_times = pre_times
        self.post_times = post_times
        self.click_magic_when_run = True
        """运行时是否点击魔法点重置窗口状态到Page级别"""
        
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
            config.sessiondict["INFO_DICT"][self.name+"_SKIP"] = f"跳过{self.name}任务"

    @staticmethod
    def back_to_home(times = 5) -> bool:
        """
        尝试从游戏内的页面返回主页
        
        返回成功与否
        """
        logging.info({"zh_CN": "尝试返回主页", "en_US":"Try back to homepage"})
        can_back_home = False
        for i in range(times):
            click(Page.MAGICPOINT, sleeptime=0.1)
            click(Page.MAGICPOINT, sleeptime=0.2)
            screenshot()
            if match(button_pic(ButtonName.BUTTON_HOME_ICON)):
                click(button_pic(ButtonName.BUTTON_HOME_ICON), sleeptime=3)
                can_back_home = True
                screenshot()
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
        """
        重复执行func1，至多times次或直到func2成立
        
        func1内部应当只产生有效操作一次或内部调用截图函数, func2判断前会先触发截图
        
        每次执行完func1后,等待sleeptime秒

        如果func2成立退出，返回true，否则返回false
        """
        # 设置times，如果传进来是None，就用config里的值
        if(times == None):
            times = config.userconfigdict["RUN_UNTIL_TRY_TIMES"]
        # 设置sleeptime，如果传进来是None，就用config里的值
        if(sleeptime == None):
            sleeptime = config.userconfigdict["RUN_UNTIL_WAIT_TIME"]
        for i in range(times):
            screenshot()
            if(func2()):
                return True
            func1()
            sleep(sleeptime)
        screenshot()
        if(func2()):
            return True
        logging.warning("run_until exceeded max times")
        return False

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
        Task.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
            times=15,
        )