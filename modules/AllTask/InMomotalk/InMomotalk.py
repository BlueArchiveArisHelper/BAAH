from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, match_pixel,
                           screenshot)


class InMomotalk(Task):
    def __init__(self, name="InMomotalk") -> None:
        super().__init__(name)

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def whether_has_red_icon(self) -> bool:
        """
        检测第一条对话旁边是否有红色标记，
        中途会重新排序，最多尝试三次，
        """
        # 考虑重新排序
        for i in range(3):
            # 点击momotalk标题位置，尝试去除弹窗
            click(self.momo_title_pos)
            # 有时候明明对话结束了，但是还是会有红标记，所以先点一下二号位刷新以下一号位的信息
            # 点第二个
            click((262, 330), sleeptime = 1.5)
            # 有时候第二个对话也会刷出来按钮，这时候也可以直接检测并点一下，加快速度，不尝试等待 (有就点，没有就不点)
            self.click_reply(only_try_once=True)
            # 点第一个
            click((263, 253))
            # 检测红标记，手动截图！
            screenshot()
            if match_pixel((638, 242), Page.COLOR_RED):
                # logging.info({"zh_CN": "检测到红色标记", "en_US": "Red marks detected"})
                return True
            # 如果在第二位检测到红标记
            if match_pixel((638, 318), Page.COLOR_RED):
                logging.info({"zh_CN": "刷新排序", "en_US": "Refresh Sorting"})
                click((623, 177))
                click((623, 177))
            else:
                # 点击重新排序
                logging.info({"zh_CN": "重新排序", "en_US": "Reorder"})
                click((623, 177))
        return False

    def click_reply(self, only_try_once = False) -> None:
        """
        点击第一条对话，点击对话框位置或者羁绊按钮

        一般是 回复-》（粉色羁绊-》蓝色进入羁绊剧情）
        """
        # 右侧往下滑动, 在头像框的位置滑
        sleep(0.5)
        # 执行两次检测按钮
        for t_time in range(2):
            swipe((727, 460), (727, 243), sleeptime=1)
            # 手动截图！
            screenshot()
            # 回复按钮 +40
            reply_button = match(button_pic(ButtonName.BUTTON_MOMOTALK_REPLY), threshold=0.87, returnpos=True)
            logging.info({"zh_CN": "回复按钮匹配度:{:.2f}".format(reply_button[2]),
                        "en_US": "Reply button matching degree :{:.2f}".format(reply_button[2])})
            if reply_button[0]:
                logging.info({"zh_CN": "检测到回复按钮", "en_US": "Reply Button Detected"})
                self.run_until(
                    lambda: click((reply_button[1][0], reply_button[1][1] + 40)),
                    lambda: not match(button_pic(ButtonName.BUTTON_MOMOTALK_REPLY), threshold=0.87)
                )
            # 羁绊按钮 +40
            partner_button = match(button_pic(ButtonName.BUTTON_MOMOTALK_PARTNER), threshold=0.87, returnpos=True)
            logging.info({"zh_CN": "羁绊按钮匹配度:{:.2f}".format(partner_button[2]),
                        "en_US": "Bond button matching degree:{:.2f}".format(partner_button[2])})
            if partner_button[0]:
                logging.info({"zh_CN": "检测到羁绊按钮", "en_US": "Bond Button Detected"})
                self.run_until(
                    lambda: click((partner_button[1][0], partner_button[1][1] + 40)),
                    lambda: not match(button_pic(ButtonName.BUTTON_MOMOTALK_PARTNER), threshold=0.87)
                )
                # 羁绊按钮后面必定有羁绊剧情按钮，等待一秒
                sleep(1.5)
                # 前往羁绊剧情按钮
                self.run_until(
                    lambda: click(button_pic(ButtonName.BUTTON_GO_PARTNER_STORY)),
                    lambda: not match(button_pic(ButtonName.BUTTON_GO_PARTNER_STORY))
                )
                sleep(2)
                # 尝试跳过剧情
                SkipStory().run()
            # 如果第一次执行没有匹配到任何按钮，睡4秒再试一次
            if not only_try_once and t_time == 0 and not reply_button[0] and not partner_button[0]:
                sleep(4)
            else:
                # 如果匹配到按钮或者是第二次执行，就不用睡了，直接break
                break

    def on_run(self) -> None:
        # 点击打开momotalk界面
        openmomo = self.run_until(
            lambda: click((172, 174)),
            lambda: match(popup_pic(PopupName.POPUP_MOMOTALK)) or match(popup_pic(PopupName.POPUP_MOMOTALK_FANHEXIE))
        )
        if not openmomo:
            logging.info({"zh_CN": "未检测到momotalk弹窗，跳过此任务",
                          "en_US": "The momotalk popup is not detected. Skip this task"})
            self.back_to_home()
            return
        # 分辨是POPUP_MOMOTALK 还是 POPUP_MOMOTALK_FANHEXIE
        momotalk_popup_fpath = PopupName.POPUP_MOMOTALK
        """
        动态匹配的标题： momotalk 或 桃信
        """
        if match(popup_pic(PopupName.POPUP_MOMOTALK_FANHEXIE)):
            momotalk_popup_fpath = PopupName.POPUP_MOMOTALK_FANHEXIE
        # 记住momotalk标题位置
        self.momo_title_pos = match(popup_pic(momotalk_popup_fpath), returnpos=True)[1]
        # 切换到对话界面
        click((170, 299), 1)
        click((170, 299), 1)
        # 按照未读的momotalk筛选
        click((507, 176), 1) # 打开筛选框
        click((508, 293))  # 日, 国际服, 国
        # 关掉筛选框，OK
        click((450, 366))  # 国，国际服
        click((450, 421))
        click((447, 475))  # 日
        # 尝试切换排序，多次后还没检测到红标记就放弃
        self.scroll_left_up()
        # 检测是否有红点，没有就退出
        has_red_icon_initial = self.whether_has_red_icon()
        if not has_red_icon_initial:
            logging.info({"zh_CN": "未检测到红点标记，跳过此任务", "en_US": "No red dot detected, skipping this task"})
            self.back_to_home()
            return
        # has_red_icon_initial 只有第一次循环开头被使用于判断
        while (has_red_icon_initial or self.whether_has_red_icon()):
            has_red_icon_initial = False
            # 处理第一个momotalk
            logging.info({"zh_CN": "处理第一条momotalk", "en_US": "Dealing with the first momotalk"})
            # 按回复框或羁绊框并跳过剧情
            self.click_reply()
            # 剧情过完可能会有个得到回忆大厅的弹窗
            sleep(1.5)
            self.run_until(
                lambda: click(self.momo_title_pos, sleeptime=0.7),
                lambda: match(popup_pic(momotalk_popup_fpath))
            )
        logging.info({"zh_CN": "momotalk处理完毕，返回主页", "en_US": "momotalk finished, go back to homepage"})
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: not match(popup_pic(momotalk_popup_fpath))
        )
        self.back_to_home()
        # 递归
        InMomotalk().run()

    def post_condition(self) -> bool:
        return self.back_to_home()