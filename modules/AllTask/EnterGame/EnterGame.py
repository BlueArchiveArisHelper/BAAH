from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config, ocr_area, logging, istr, CN, EN, screenshot
# =====
from .Loginin import Loginin
from .CloseInform import CloseInform

class EnterGame(Task):
    """
    确保游戏打开并处在ba主页的任务

    当 strict_mode 为False，不会记录资源，不会切换页面一次来检查是否要重新登录
    """
    def __init__(self, strict_mode=True, name="EnterGame" , pre_times = 1, post_times = 10) -> None:
        super().__init__(name, pre_times, post_times)
        self.strict_mode = strict_mode
    
    def record_resources(self):
        """
        记录主页中的资源
        """
        if not self.strict_mode:
            return
        # 记录主页中的资源
        power_num = ocr_area((483, 17), (582, 56))[0]
        # print("体力: ", power_num)
        credit_num = ocr_area((668, 19), (812, 59))[0]
        # print("信用点: ", credit_num)
        diamond_num = ocr_area((863, 21), (973, 60))[0]
        # print("钻石: ", diamond_num)
        config.sessiondict["BEFORE_BAAH_SOURCES"] = {"power": power_num, "credit": credit_num, "diamond": diamond_num}
     
    def pre_condition(self) -> bool:
        return True
    
     
    def on_run(self) -> None:
        # 闲置状态下会隐藏主页UI，随便点两下试图唤起UI（如果在游戏内的话）
        click(Page.MAGICPOINT)
        click(Page.MAGICPOINT)
        screenshot()
        has_recorded = False
        if not self.has_popup() and Page.is_page(PageName.PAGE_HOME):  
            # 没有社区弹窗，而且直接就在主页的话，直接记录资源  
            self.record_resources()
            has_recorded = True
        if match(button_pic(ButtonName.BUTTON_HOME_ICON)):
            return_home = self.back_to_home()
            if return_home:
                # 如果成功返回主页，记录资源
                self.record_resources()
                has_recorded = True
        if has_recorded:
            if not self.strict_mode:
                # 非严格模式下，确保回到主页即可
                return
            # 如果已经在游戏主页，判断是否服务器刷新需要重新登录
            logging.info(istr({
                CN: "检查是否需要重新登录",
                EN: "Check if need to re-login"
            }))
            can_go_to_daily_task_page = self.run_until(
                lambda: click((66, 237)),
                lambda: Page.is_page(PageName.PAGE_TASK_CENTER),
                times=4
            )
            if can_go_to_daily_task_page:
                logging.info(istr({
                    CN: "无需重新登录",
                    EN: "No need to re-login"
                }))
                # 如果可以进入日常任务页，说明已经在主页
                self.back_to_home()
                return
        # 如果第一步骤无法回到主页或识别主页icon
        # 登录流程
        Loginin().run()
        CloseInform().run()
        # 如果登入到游戏，记录资源
        self.record_resources()
        
    
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_HOME)