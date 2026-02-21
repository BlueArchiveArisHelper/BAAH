from modules.utils.log_utils import logging
import random
import time
import requests
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.configs.MyConfig import config

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InEvent.EventQuest import EventQuest
from modules.AllTask.InEvent.EventStory import EventStory
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, screenshot,
                           check_app_running, open_app, get_now_running_app_entrance_activity, get_now_running_app, istr, CN, EN)


class InEvent(Task):
    def __init__(self, name="InEvent") -> None:
        super().__init__(name)
        self.try_enter_times = 2
        self.next_sleep_time = 0.1
        # 是否有活动但是已经结束
        self.has_event_but_closed = False
        self.quest_button_xy = (965, 98)

    def pre_condition(self) -> bool:
        # 通过get请求https://arona.diyigemt.com/api/v2/image?name=%E5%9B%BD%E9%99%85%E6%9C%8D%E6%B4%BB%E5%8A%A8
        # 获取国际服活动，判断是否有活动

        # request_url = "https://arona.diyigemt.com/api/v2/image?name=%E5%9B%BD%E9%99%85%E6%9C%8D%E6%B4%BB%E5%8A%A8"
        # response = requests.get(request_url)
        # if response.status_code == 200:
        #     if len(response.json()['data']) != 0:
        #         logging.info({"zh_CN": "存在国际服活动", "en_US": "Presence of international dress events"})
        #         self.try_enter_times = 20
        #         return Page.is_page(PageName.PAGE_HOME)
        #     else:
        #         logging.warn({"zh_CN": "不存在国际服活动", "en_US": "There are no international dress events"})
        #         self.try_enter_times = 0
        #         return False
        return self.back_to_home()

    def try_goto_event(self):
        """
        点击滚动栏，前往活动页面
        """
        if Page.is_page(PageName.PAGE_FIGHT_CENTER):
            # 尝试前往活动页面
            logging.info({"zh_CN": "尝试前往活动页面", "en_US": "Try going to the event page"})
            self.run_until(
                lambda: click((105, 162), sleeptime=1.5),
                lambda: not Page.is_page(PageName.PAGE_FIGHT_CENTER)
            )
        else:
            # 如果不在Fight Center页面，返回主页然后来到Fight Center页面
            logging.warn({"zh_CN": "页面发生未知偏移，尝试修正", "en_US": "Meets unknown page, try to fix it"})
            self.back_to_home()
            self.run_until(
                lambda: click((1196, 567)),
                lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
            )
            # 睡眠一段时间
            sleep(self.next_sleep_time)
            self.next_sleep_time += 2
            logging.info({"zh_CN": "尝试前往活动页面", "en_US": "Try going to the event page"})
            self.run_until(
                lambda: click((105, 162), sleeptime=1.5),
                lambda: not Page.is_page(PageName.PAGE_FIGHT_CENTER)
            )

    def judge_whether_available_event(self):
        """
        判断页面是否是一个有效的活动页面
        """
        # 判断是否是在ba游戏里
        if not check_app_running(config.userconfigdict['ACTIVITY_PATH']) or get_now_running_app_entrance_activity() != \
                config.userconfigdict['ACTIVITY_PATH'] or "webview" in get_now_running_app().lower():
            logging.warn({"zh_CN": "跳转出了游戏，尝试重新进入游戏",
                          "en_US": "Try to re-enter the game after jumping out of the game"})
            open_app(config.userconfigdict['ACTIVITY_PATH'])
            sleep(1.5)
            if not check_app_running(
                    config.userconfigdict['ACTIVITY_PATH']) or get_now_running_app_entrance_activity() != \
                    config.userconfigdict['ACTIVITY_PATH'] or "webview" in get_now_running_app().lower():
                logging.error({"zh_CN": "重新进入游戏失败", "en_US": "Failed to re-enter the game"})
                raise Exception("重新进入游戏失败")
            logging.info({"zh_CN": "重新进入游戏成功", "en_US": "Successfully re-entered the game"})
            screenshot()  # 截图让后面继续判断
        if not Page.is_page(PageName.PAGE_EVENT):
            # 可能首次进入活动，有活动剧情
            SkipStory(pre_times=5).run()
        click(Page.MAGICPOINT, sleeptime=0.3)
        click(Page.MAGICPOINT, sleeptime=0.3)
        screenshot()
        # 判断左上角标题
        if not Page.is_page(PageName.PAGE_EVENT):
            return False
        # 图片匹配深色的QUEST标签
        self.quest_button_xy = (965, 98)
        # 预先点击一次假设的 Quest Tab 位置
        click(self.quest_button_xy)
        screenshot()
        matchpic = self.run_until(
            lambda: click(self.quest_button_xy),
            lambda: match(button_pic(ButtonName.BUTTON_EVENT_QUEST_SELLECTED)),
            times=2
        )
        # 修复 白鸟区修复活动 Quest关卡在tab最左侧导致匹配失败问题
        if not matchpic:
            # 点下左边Quest tab
            self.quest_button_xy = (922, 98)
            matchpic = self.run_until(
                lambda: click(self.quest_button_xy),
                lambda: match(button_pic(ButtonName.BUTTON_EVENT_QUEST_SELLECTED)),
                times=2
            ) 
        logging.info({"zh_CN": f"QUEST按钮匹配结果: {matchpic}",
                      "en_US": f"QUEST button matching result: {matchpic}"})
        if not matchpic:
            logging.warn({"zh_CN": "此页面不存在活动Quest", "en_US": "No event Quest on this page"})
            return False
        # 通过数字识别关卡数字，判断活动是否已结束
        # event_res为最终判断活动有没有开放还是进入到领取奖励阶段
        event_res = False
        screenshot()
        reslist = ocr_area((695, 416), (752, 699), multi_lines=True)
        for res in reslist:
            try:
                res_num = int(res[0])
                event_res = True
                break
            except:
                continue
        # # 判断左下角时间
        time_res = ocr_area((175, 566), (552, 593))
        # if len(time_res[0])==0:
        #     return False
        # # '2023-12-2603:00~2024-01-0902:59'
        logging.info({"zh_CN": f"识别活动时间: {time_res}",
                      "en_US": f"Identification activity time: {time_res}"})
        # # 分割出结束时间
        # # 取最后15个字符
        # if len(time_res[0]) < 15:
        #     logging.error({"zh_CN": "活动时间字符串长度不足15", "en_US": "Activity time string less than 15"})
        #     return False
        # end_time = time_res[0][-15:]

        # # 判断活动是否已结束
        # if len(end_time) != 15:
        #     logging.error({"zh_CN": "活动时间字符串长度不足15", "en_US": "Activity time string less than 15"})
        #     return False
        # # 将这个时间转成时间对象
        # all_possible_format = ["%Y-%m-%d%H:%M", "%Y.%m.%d%H:%M", "%m/%d/%Y%H:%M"]
        # end_time_struct = None
        # for format in all_possible_format:
        #     try:
        #         end_time_struct = time.strptime(end_time, format)
        #         break
        #     except ValueError:
        #         print(f"时间解析失败: {end_time} {format}")
        #         continue
        # if not end_time_struct:
        #     # 时间解析失败直接认为它失败
        #     logging.error({"zh_CN": "时间解析失败，默认判断此活动已结束", "en_US": "Time parsing failed, it is judged that this activity has ended by default"})
        #     return False
        # logging.info(f'结束时间: {time.strftime("%Y-%m-%d %H:%M:%S", end_time_struct)}')
        # # 获取本地时间
        # local_time_struct = time.localtime()
        # # 输出字符串
        # logging.info(f'本地时间: {time.strftime("%Y-%m-%d %H:%M:%S", local_time_struct)}')
        # # 检测local_time_struct是否在end_time_struct之前
        # if local_time_struct > end_time_struct:
        #     logging.info({"zh_CN": "此活动已结束", "en_US": "This event has ended"})
        #     return False

        end_date = time_res[0][-16:]
        if event_res:
            logging.info({"zh_CN": "活动开放中", "en_US": "The event is open"})
            # 避免重复输出
            config.append_noti_sentence(key="EVENT_DATE", sentence=istr({
                CN: f"活动开放中，结束日期: {end_date}",
                EN: f"Event open, end date: {end_date}"
            }))
            return True
        else:
            logging.error({"zh_CN": "未能识别有效活动关卡，判断活动已结束",
                           "en_US": "Could not recognize the valid event level, and the event is judged to be over"})
            self.has_event_but_closed = True
            # 避免重复输出
            config.append_noti_sentence(key="EVENT_DATE", sentence=istr({
                CN: f"活动领取奖励阶段，结束日期: {end_date}",
                EN: f"Event is during receive rewards stage, end date: {end_date}"
            }))
            return False

    def get_biggest_level(self):
        """
        通过下滑到底ocr获取最大关卡数

        -1表示没有找到
        """
        self.scroll_right_down()
        sleep(1)
        screenshot()
        reslist = ocr_area((695, 416), (752, 699), multi_lines=True)
        temp_max = -1
        logging.info({"zh_CN": "ocr结果: " + str(reslist), "en_US": "ocr result: " + str(reslist)})
        # 将每一个字母尝试转换成数字，如果是数字就比较目前最大
        for res in reslist:
            try:
                # 最大不过14
                temp_max = min(max(temp_max, int(res[0])), 14)
            except:
                pass
        return temp_max

    def on_run(self) -> None:
        # 进入Fight Center, 这里离开了主页之后就狂点活动标
        self.run_until(
            lambda: click((1196, 567)),
            lambda: not Page.is_page(PageName.PAGE_HOME),
        )
        # 狂点活动标
        for i in range(15):
            click((35, 110), sleeptime=0.2)
        click(Page.MAGICPOINT)
        click(Page.MAGICPOINT)
        # 尝试进入Event
        enter_event = self.run_until(
            lambda: self.try_goto_event(),
            lambda: self.judge_whether_available_event() or self.has_event_but_closed,
            times=self.try_enter_times
        )
        if self.has_event_but_closed:
            logging.warn({"zh_CN": "存在活动但是已经结束", "en_US": "Contains events but has ended"})
            return
        if not enter_event:
            logging.warn({"zh_CN": "未能成功进入活动Event页面", "en_US": "Failed to enter the event Event page"})
            return
        logging.info({"zh_CN": "成功进入Event页面", "en_US": "Successfully entered the Event page"})
        today = time.localtime().tm_mday

        # 检测并推剧情，如果已经进入过活动一次了，就不用再推剧情了
        if config.userconfigdict["AUTO_EVENT_STORY_PUSH"] and not config.sessiondict["HAS_ENTER_EVENT"]:
            # 点击Story标签
            click((766, 98))
            click((766, 98))
            story_max_level = self.get_biggest_level()
            EventStory(max_level=story_max_level).run()
        # 推图任务，如果已经进入过活动一次了，就不用再推图了
        if config.userconfigdict["AUTO_PUSH_EVENT_QUEST"] and not config.sessiondict["HAS_ENTER_EVENT"]:
            # 点击Quest标签
            click(self.quest_button_xy)
            click(self.quest_button_xy)
            logging.info({"zh_CN": "检查活动关卡是否推完", "en_US": "Check if the active level has been pushed"})
            maxquest = self.get_biggest_level()
            if maxquest == -1:
                logging.warn({"zh_CN": "未能识别活动关卡，跳过推图直接进行扫荡",
                              "en_US": "Failed to recognize the event level, "
                                       "skip the push map and go directly to the sweep"})
            else:
                maxquest_ind = maxquest - 1
                logging.info({"zh_CN": f"最大关卡: {maxquest}，开始检测是否需要推图",
                              "en_US": f"Max level: {maxquest}, start to detect whether the tweet is needed"})
                # 设置一个推maxquest_ind关卡0次的任务
                EventQuest([[maxquest_ind, 0]], explore=True, raid=False, collect=False, quest_button_xy=self.quest_button_xy).run()
        # 扫荡任务
        if config.userconfigdict["EVENT_QUEST_LEVEL"] and len(config.userconfigdict["EVENT_QUEST_LEVEL"]) != 0:
            # 可选任务队列不为空时
            quest_loc = today % len(config.userconfigdict['EVENT_QUEST_LEVEL'])
            # 得到要执行的QUEST LIST
            # [[10, -1],[11, -1]]
            quest_list = config.userconfigdict['EVENT_QUEST_LEVEL'][quest_loc]
            # 序号转下标
            quest_list_2 = [[x[0] - 1, x[1], *x[2:]] for x in quest_list]
            # do Event QUEST
            EventQuest(quest_list_2, explore=False, raid=True, collect=True, quest_button_xy=self.quest_button_xy).run()

    def post_condition(self) -> bool:
        config.sessiondict["HAS_ENTER_EVENT"] = True
        return self.back_to_home()