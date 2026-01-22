from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InCafe.InviteStudent import InviteStudent
from modules.AllTask.Task import Task
from modules.utils.log_utils import logging
from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, config, match_pixel, istr, CN, EN

# =====

from .CollectPower import CollectPower
from .TouchHead import TouchHead
from .BuyTicket import BuyTicket


class InCafe(Task):
    def __init__(self, name="InCafe", pre_times = 3, post_times = 3) -> None:
        super().__init__(name, pre_times, post_times)
        self.collect = config.userconfigdict["CAFE_COLLECT"]
        self.touch = config.userconfigdict["CAFE_TOUCH"]

    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    def cafe_process(self, invite_seq, is_buy_ticket, invite_seq_buy):
        """一处咖啡馆除了领取体力之外的所有流程"""
        # 摸头  -> 邀请学生 --> 摸头 --> 买邀请卷 --> 邀请学生 --> 摸头
        #    |-x-> 结束             |        |-x->结束 |    e-> 结束
        #                |-e->------|        |-e-------|
        # x: 设置为否
        # e: 操作失败
        if not self.touch:
            logging.info(istr({
                CN: "设置的咖啡馆不摸头，结束",
                EN: "the setup file sets the cafe without touching head, ending"
            }))
            return
        # 摸头
        TouchHead().run()
        # 邀请学生+摸头
        if invite_seq != 0:
            invite_cafe1 = InviteStudent(invite_seq-1)
            invite_cafe1.run()
            if invite_cafe1.status != Task.STATUS_SUCCESS:
                logging.warn(istr({
                    CN: "邀请学生失败，跳过第二次摸头",
                    EN: "Failed to invite student, skip the second touch head"
                }))
            else:
                TouchHead(try_touch_epoch=1).run()
        else:
            logging.info(istr({
                CN: "设置的普通邀请卷不邀请学生，判断是否购买邀请卷",
                EN: "the setup file sets the cafe without inviting student, check whether to buy invite ticket"
            }))
        
        # 买邀请卷+邀请学生+摸头
        if not is_buy_ticket:
            logging.info(istr({
                CN: "设置的咖啡馆不购买邀请券，结束",
                EN: "the setup file sets the cafe without buying invite ticket, ending"
            }))
            return
        logging.info(istr({
            CN: "开始购买邀请券",
            EN: "Start to buy invite ticket"
        }))
        buy_ticket = BuyTicket()
        buy_ticket.run()
        if buy_ticket.status != Task.STATUS_SUCCESS:
            logging.warn(istr({
                CN: "购买邀请券失败，尝试直接使用",
                EN: "Failed to buy invite ticket， try to use directly"
            }))
        if invite_seq_buy != 0:
            invite_cafe1_buy = InviteStudent(invite_seq_buy-1, buy_ticket_used=True)
            invite_cafe1_buy.run()
            if invite_cafe1_buy.status != Task.STATUS_SUCCESS:
                logging.warn(istr({
                    CN: "邀请学生失败，结束",
                    EN: "Failed to invite student, 结束"
                }))
                return
            else:
                TouchHead(try_touch_epoch=1).run()
        else:
            logging.info(istr({
                CN: f"设置的购买邀请卷不邀请学生，结束",
                EN: f"The setup file sets the cafe without inviting student with bought invite ticket, ending"
            }))




    def on_run(self) -> None:
        # 进入咖啡厅
        self.run_until(
            # 恰好是主页中的咖啡厅按钮，而又不是咖啡厅里的编辑按钮
            lambda: click((116, 687)) and click(Page.MAGICPOINT, sleeptime=1.5),
            lambda: Page.is_page(PageName.PAGE_CAFE),
        )
        # 清除"今天到场的学生"弹窗
        self.clear_popup()
        # 可能进入编辑模式，右上退出编辑模式
        click((1171, 95))
        # 收集体力
        if self.collect:
            CollectPower().run()
        else:
            logging.info(istr({
                CN: "设置的咖啡馆不收集体力",
                EN: "The setup file sets the cafe without collecting power"
            })) 
        # 处理第一个咖啡厅
        self.cafe_process(
            invite_seq=config.userconfigdict["CAFE1_INVITE_SEQ"],
            is_buy_ticket=config.userconfigdict["CAFE1_BUY_INVITE_TICKET"],
            invite_seq_buy=config.userconfigdict["CAFE1_BUY_INVITE_SEQ"]
        )
        # 清除弹窗
        self.clear_popup()
        # 检测是否有第二个咖啡厅
        if not match(button_pic(ButtonName.BUTTON_CAFE_SET_ROOM)):
            logging.info(istr({
                CN: "没有识别第二个咖啡厅，跳过第二个咖啡厅环节",
                EN: "No second cafe is ocr, skip the part of entering the second cafe"
            }))
            return
        # 进入第二个咖啡厅
        logging.info({"zh_CN": "进入第二个咖啡厅", "en_US": "Entering the second cafe"})
        click(button_pic(ButtonName.BUTTON_CAFE_SET_ROOM), sleeptime=1)
        click((247, 165))
        # 清除弹窗
        self.clear_popup()
        # 处理第二个咖啡厅
        self.cafe_process(
            invite_seq=config.userconfigdict["CAFE2_INVITE_SEQ"],
            is_buy_ticket=config.userconfigdict["CAFE2_BUY_INVITE_TICKET"],
            invite_seq_buy=config.userconfigdict["CAFE2_BUY_INVITE_SEQ"]
        )

    def post_condition(self) -> bool:
        return self.back_to_home()