
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP
from modules.utils.log_utils import logging

class BuyAP(Task):
    def __init__(self, name="BuyAP") -> None:
        super().__init__(name)
        # 主页右上角恒白点
        self.HOME_POINT = (1026, 57)
        self.COLOR_HOME_WHITE = ((240, 240, 240),(250, 250, 250))

     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
     
    def on_run(self) -> None:
        # 打开购买弹窗
        res = self.run_until(
            lambda: click((616, 38)),
            lambda: match(button_pic(ButtonName.BUTTON_CONFIRMY)),
            sleeptime=2
        )
        if not res:
            logging.warn(istr({CN: "未找到购买按钮", EN: "Can't find buy button", JP: "購入ボタンが見つかりません"}))
            return
        # 识别购买限制
        ocr_content = ocr_area((496, 399), (572, 428))[0]
        logging.info(istr({CN: f"识别单价: {ocr_content}", EN: f"Recognize price: {ocr_content}", JP: f"価格を認識する: {ocr_content}"}))
        # 只保留ocr_content中的数字
        price = "".join(filter(str.isdigit, ocr_content))
        try:
            price = int(price)
            logging.info(istr({CN: f"识别单价为: {price}", EN: f"Recognize price is: {price}", JP: f"価格を認識するわ: {price}"}))
            max_price = config.userconfigdict.get("BUY_AP_MAX_PRICE")
            logging.info(istr({CN: f"最高单价限制为: {max_price}", EN: f"Max price limit is: {max_price}", JP: f"最高価格制限は: {max_price}"}))
        except:
            logging.error(istr({CN: "识别单价失败", EN: "Recognize price failed", JP: "価格の認識に失敗しました"}))
            return
        # 点击加号
        if price <= config.userconfigdict.get("BUY_AP_MAX_PRICE"):
            for t in range(config.userconfigdict.get("BUY_AP_ADD_TIMES") - 1):
                click((804, 346))
            # 点击购买，清除弹窗，主页的判断点比较特殊
            self.run_until(
                lambda: click(button_pic(ButtonName.BUTTON_CONFIRMY)) or (click(Page.MAGICPOINT) and click(Page.MAGICPOINT)),
                lambda: match_pixel(self.HOME_POINT, self.COLOR_HOME_WHITE)
            )
        else:
            # 价格超过限制，不购买，清除弹窗
            logging.info(istr({CN: "价格超过限制，不购买", EN: "Price exceeds the limit, not buy", JP: "価格が制限を超えているため、購入しない"}))
            self.run_until(
                lambda: click(Page.MAGICPOINT),
                lambda: match_pixel(self.HOME_POINT, self.COLOR_HOME_WHITE)
            )

     
    def post_condition(self) -> bool:
        return self.back_to_home()