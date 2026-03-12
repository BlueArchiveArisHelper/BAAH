
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel
from modules.utils.log_utils import logging

class CollectGrandAssaultReward(Task):
    def __init__(self, name="CollectGrandAssaultReward") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_GRAND_ASSAULT)
    
    def click_collect_button(self):
        self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_COLLECT), threshold=0.8),
            lambda: match(button_pic(ButtonName.BUTTON_COLLECT), returnpos=True)[2] < match(button_pic(ButtonName.BUTTON_COLLECT_GRAY), returnpos=True)[2]
        )
     
    def on_run(self) -> None:
        # 关闭界面
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
        )
        
        # 打开领取界面
        open_collect_popup = self.run_until(
            lambda: click((1182, 673)),
            lambda: not match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
        )
        if not open_collect_popup:
            logging.warn({"zh_CN": "大决战无领取页面", "en_US":"There is no collect page in Grand Assault"})
            return
        logging.info({"zh_CN": "领取大决战奖励", "en_US": "Claim Grand Assault Rewards"})
        # 切到奖励
        click((912, 170))
        click((912, 170))
        
        # 这里领取完奖励会有奖励弹窗，但是第一栏和第二栏只会领取其中一个，直接用最后的关闭界面即可清除所有遮罩
        # 第一栏
        click((235, 241))
        self.click_collect_button()
        # 第二栏
        click((226, 310))
        self.click_collect_button()
        # 国服多了第三栏
        click((238, 374))
        self.click_collect_button()

        
        # 关闭界面
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE)
        )

     
    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_GRAND_ASSAULT)