from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)

def try_to_solve_new_section(need_to_wait_more = False, new_button_threshold = 0.9):
        """
        尝试处理完当前章节所有可点的New小节，此操作会退出小节选择页面返回上级
        """
        # 来到小节页面
        sleep(3)  # 等动画
        initial_enter = True
        while True:
            screenshot()
            # 点击New章节
            new_bool, new_pos, new_val = match(button_pic(ButtonName.BUTTON_NEW_STORY_LEVEL), threshold=new_button_threshold, returnpos=True)
            if new_bool:
                logging.info({"zh_CN": "检测到新小节，点击进入", "en_US": "New section detected, tap to enter"})
                # 点击入场
                enter_popup = Task.run_until(
                    lambda: click([new_pos[0] + 467, new_pos[1] + 46]),
                    lambda: match(popup_pic(PopupName.POPUP_CHAPTER_INFO)),
                    times=3
                )
            elif not new_bool and initial_enter:
                # 如果第一次进入循环但是没有匹配上New标识，那么可能已经推到了最后一节，但是New无法识别出来
                # 手动点顶部的那一节
                logging.warn({"zh_CN": "暂未能匹配到New标识符，尝试进入最顶部小节",
                              "en_US": "Cannot match New button, try to enter the top section manually"})
                # 点击入场
                enter_popup = Task.run_until(
                    lambda: click((1170, 254)),
                    lambda: match(popup_pic(PopupName.POPUP_CHAPTER_INFO)),
                    times=3
                )
            else:
                # 返回上级到主线剧情页面，离开剧情页面
                break
            # 如果匹配到章节资讯弹窗
            if enter_popup:
                # 点击开始
                logging.info({"zh_CN": "点击进入小节", "en_US": "Tap to enter the section"})
                Task.run_until(
                    lambda: click((637, 518)),
                    lambda: not match(popup_pic(PopupName.POPUP_CHAPTER_INFO)),
                )
                # 进入章节后先剧情（可能会有双重剧情），然后可能有战斗
                skip_story = SkipStory()
                logging.info(istr({
                    CN: "等待跳过剧情",
                    EN: "Waiting to skip the story"
                }))
                if need_to_wait_more:
                    # 序幕考虑等久一点
                    Task.run_until(
                        lambda: click(Page.MAGICPOINT, sleeptime=1),
                        lambda: skip_story.pre_condition(), # 这里面有十次判断
                        times=3
                    )
                skip_story.run()
                # 多重剧情
                for i in range(5):
                    sleep(2)
                    skip_story_again = SkipStory()
                    if skip_story_again.pre_condition():
                        logging.info(istr({
                            CN: "检测到多重剧情，开始跳过",
                            EN: "Multiple stories detected, start skipping"
                        }))
                        skip_story_again.run()
                    else:
                        break
                logging.info(istr({
                    CN: "剧情部分结束",
                    EN: "The story is over"
                }))
                # 尝试回到选择小节页面，后面战斗完也要考虑这个，不过那里写在FightQuest里面了
                back_to_select = Task.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: match(page_pic(PageName.PAGE_STORY_SELECT_SECTION)) and match_pixel(Page.MAGICPOINT,
                                                                                                Page.COLOR_WHITE),
                    times=4
                )
                if not back_to_select:
                    # 如果跳过剧情后没有回到小节选择页面，那么就是有战斗，这里传入in_main_story_mode=True让FightQuest知道不需要检测最后的奖励页面
                    # 如果走格子，就报错，目前不支持
                    if Page.is_page(PageName.PAGE_GRID_FIGHT):
                        raise Exception("不支持走格子战斗")
                    logging.info({"zh_CN": "检测到战斗，开始战斗", "en_US": "Battle detected and battle started"})
                    # 编辑部队这里左上角页面名字不一样
                    # 点击右下角开始战斗按钮
                    click((1158, 662))
                    click((1158, 662))
                    # 直接开始战斗，然后直接到AUTO切换阶段，最后不用领取奖励判断
                    FightQuest(backtopic=lambda: match(page_pic(PageName.PAGE_STORY_SELECT_SECTION)),
                               start_from_editpage=False, in_main_story_mode=True).run()
            else:
                raise Exception("未匹配到章节资讯弹窗，该剧情可能要解锁主线关卡")
            # 回到小节列表页面，新的NEW button会有一段出现动画，这里确保动画结束
            # 清除弹窗
            Task.clear_popup()
            logging.info(istr({
                CN: "等待5s",
                EN: "Wait for 5s"
            }))
            # 等动画 最多5s
            Task.run_until(
                lambda: click(Page.MAGICPOINT, sleeptime=0.1),
                lambda: match(button_pic(ButtonName.BUTTON_NEW_STORY_LEVEL), threshold=new_button_threshold),
                sleeptime=1,
                times=5
            )
            initial_enter = False
        # 返回上级到主线剧情页面，离开剧情小节页面
        Task.run_until(
            lambda: click(Page.TOPLEFTBACK),
            lambda: not Page.is_page(PageName.PAGE_STORY_SELECT_SECTION),
            times=4,
            sleeptime=2
        )

def goto_story_page():
    """从主页到剧情总览页面"""
    Task.run_until(
        lambda: click((1196, 567)),
        lambda: Page.is_page(PageName.PAGE_FIGHT_CENTER),
        times=4,
        sleeptime=2
    )
    # 进入总剧情页面
    Task.run_until(
        lambda: click(page_pic(PageName.PAGE_FIGHT_CENTER)),
        lambda: not match(page_pic(PageName.PAGE_FIGHT_CENTER)),
        times=3,
        sleeptime=2
    )
    logging.info({"zh_CN": "进入剧情页面", "en_US": "Enter Story Page"})
    sleep(2)