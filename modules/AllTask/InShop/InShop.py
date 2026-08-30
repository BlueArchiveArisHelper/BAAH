 
from modules.utils.I18nstr import CN, EN, istr
from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InShop.ContestItems import ContestItems
from modules.AllTask.InShop.NormalItems import NormalItems
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task



import numpy as np

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, get_correct_asset, AssetMappingKeys

class InShop(Task):
    def __init__(self, name="InShop") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
     
    def on_run(self) -> None:
        # 进入商店
        shop_entry_pos = get_correct_asset(config, AssetMappingKeys.SHOP_ENTRY_POS)
        self.run_until(
            lambda: click(shop_entry_pos),
            lambda: Page.is_page(PageName.PAGE_SHOP),
        )
        # 判断config里的开关是否开启
        if not config.userconfigdict["SHOP_NORMAL_SWITCH"]:
            logging.info(istr({
                CN: "设置中未开启普通商店购买",
                EN: "Normal shop purchase is not enabled in settings"
            }))
        else:
            NormalItems().run()
        # 判断config里的开关是否开启
        if not config.userconfigdict["SHOP_CONTEST_SWITCH"]: 
            logging.info(istr({
                CN: "设置中未开启竞技场商店购买",
                EN: "Contest shop purchase is not enabled in settings"
            }))
            self.back_to_home()
            return
        switchres = self.run_until(
            lambda: click(button_pic(ButtonName.BUTTON_SHOP_CONTEST_W)),
            lambda: match(button_pic(ButtonName.BUTTON_SHOP_CONTEST_B)),
            times=3
        )
        if not switchres:
            # 尝试滑动左侧列表往下
            swipe((100, 467),(100, 192), durationtime=0.5)
            switchres = self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_SHOP_CONTEST_W)),
                lambda: match(button_pic(ButtonName.BUTTON_SHOP_CONTEST_B)),
                times=3
            )
        if not switchres:
            logging.error({"zh_CN": "切换到竞技场商店失败，中止任务", "en_US":"Switch to contest shop failed, abort task"})
            return
        ContestItems().run()
        
        # 返回主页
        self.back_to_home()

    def post_condition(self) -> bool:
        return self.back_to_home()
