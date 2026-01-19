from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, istr, CN, EN


class InviteStudent(Task):
    """
    stuind 从0开始，邀请的学生的下标
    """

    def __init__(self, stuind, invite_button_pos = None, buy_ticket_used = False, name="InviteStudent") -> None:
        super().__init__(name)
        self.stuind = abs(stuind)
        # 初始status为失败，只有成功邀请后才改为成功
        self.status = self.STATUS_ERROR
        if invite_button_pos is None:
            self.invite_button_pos = (850, 652)
        else:
            self.invite_button_pos = invite_button_pos
        # 花钱购买了票卷的邀请的话，邀请弹窗确认按钮是黄色
        self.buy_ticket_used = buy_ticket_used
        if self.buy_ticket_used:
            self.confirm_invite_button_pic = ButtonName.BUTTON_CONFIRMY
        else:
            self.confirm_invite_button_pic = ButtonName.BUTTON_CONFIRMB

    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_CAFE)

    def on_run(self) -> None:
        while(1):
            # 打开邀请界面
            open_momo = self.run_until(
                lambda: click(self.invite_button_pos),
                lambda: match(popup_pic(PopupName.POPUP_MOMOTALK)) or match(popup_pic(PopupName.POPUP_MOMOTALK_FANHEXIE)),
                times=3
            )
            if not open_momo:
                logging.error({"zh_CN": "咖啡馆邀请界面打开失败, 跳出邀请任务",
                            "en_US": "Failed to open the cafe invite interface, jump out of the invitation task"})
                return
            # 打开确认弹窗
            # 默认邀请第一个学生，一页有5个学生
            logging.info(istr({
                CN: f"邀请下标第{self.stuind}个学生",
                EN: f"Invite the index {self.stuind}th student"
            }))
            # 邀请 直到出现确认按钮
            select_stu = ScrollSelect(abs(self.stuind), 186, 264, 576, clickx = 787, hasexpectimage=lambda: match(button_pic(self.confirm_invite_button_pic)))
            select_stu.run()
            if not select_stu.hasexpectimage():
                logging.error(istr({
                    CN: "邀请学生界面无法点击到确认按钮，退出邀请任务",
                    EN: "The invitation student interface cannot click the confirm button, quit the invitation task"
                }))
                return
            if config.userconfigdict["CAFE_INVITE_SAME_NAME_DELAY"]:
                # 需要考虑是否有同名学生 也就是弹窗是否是通知弹窗
                if not match(popup_pic(PopupName.POPUP_NOTICE)):
                    # 不是通知弹窗，发生同名，需要将邀请下标顺延
                    if config.userconfigdict["CAFE_INVITE_SAME_NAME_DELAY_REVERSE"]:
                        # 逆向顺延
                        self.stuind -= 1
                    else:
                        # 顺序顺延
                        self.stuind += 1
                    logging.warn(istr({
                        # 打印下标
                        CN: f"邀请的学生已经在咖啡馆中, 邀请下标顺延: {self.stuind}",
                        EN: f"The invited student is already in the cafe, invite index number update: {self.stuind}"
                    }))
                    self.clear_popup()
                    # 从头邀请
                    continue
            # 其他情况退出while循环
            break
        # 确认，直到看不见通知确认按钮
        self.run_until(
            lambda: click(button_pic(self.confirm_invite_button_pic)),
            lambda: not match(button_pic(self.confirm_invite_button_pic))
        )
        self.status = self.STATUS_SUCCESS

    def post_condition(self) -> bool:
        self.clear_popup()
        return Page.is_page(PageName.PAGE_CAFE)