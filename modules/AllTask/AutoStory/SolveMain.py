from modules.utils.log_utils import logging

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.SubTask.SkipStory import SkipStory
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
from modules.AllTask.Task import Task
from modules.AllTask.AutoStory.StoryHelper import try_to_solve_new_section, goto_story_page

from modules.utils import (click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot,
                           match_pixel, istr, CN, EN)


class SolveMain(Task):
    """
        主线剧情自动化

        剧情总页-主线剧情（篇，章）-小节目录列表 PAGE_STORY_SELECT_SECTION.png 
    """

    def __init__(self, name="SolveMain") -> None:
        super().__init__(name)
        self.yellow_points = [
            (975, 297),
            (939, 359),
            (903, 422),
            (866, 485),
        ]
        # 黄色提示点的bgr值
        self.yellow_bgr = ((0, 170, 250), (30, 200, 255))

    

    # def recognize_max_chapter(self):
    #     """
    #     在主线剧情页面识别最大的章节数
    #     """
    #     self.scroll_to_right()
    #     screenshot()
    #     lines = ocr_area((212, 296), (793, 574), multi_lines=True)
    #     logging.info(f"ocr: {lines}")
    #     maxnum = 0
    #     for line in lines:
    #         if len(line[0]) >= 5 and line[0][3] == "." and line[0][4].isdigit():
    #             maxnum = max(maxnum, int(line[0][4]))
    #         # 国服直接以数字开头
    #         if len(line[0]) >= 2 and line[0][0].isdigit() and line[0][1] == ".":
    #             maxnum = max(maxnum, int(line[0][0]))
    #     logging.info({"zh_CN": f"最大篇章数为{maxnum}", "en_US": f"The maximum number of chapters is {maxnum}"})
    #     return maxnum

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def on_run(self) -> None:
        goto_story_page()
        # 进入主线剧情
        click((359, 368), sleeptime=0.5)
        click((359, 368), sleeptime=0.5)
        click((359, 368), sleeptime=1)
        # 可能在最终篇页面，点击左上角返回到Vol主线篇章选择页面
        self.run_until(
            lambda: click((84, 111)),
            lambda: not match_pixel((84, 111), [(0, 0, 200), (255, 255, 255)]) # 主要比较第三位，白色按钮是244，淡蓝色背景是168
        )
        logging.info({"zh_CN": "进入主线剧情", "en_US": "Enter the main storyline"})
        self.scroll_to_left()
        # 设置一共10篇主线 x:347, 611 y: 291, 415
        for i in range(10):
            # 点下下每篇的章节，然后看右侧黄点
            y_click = [291, 415] # 高度 上下
            x_click = [327, 592] # 滑动到最左，和最右。两个EX剧情的格子中心左右坐标
            offset_lr = i%2 # 0左1右
            if i !=0 and offset_lr == 0:
                # 往右翻页
                ScrollSelect.compute_swipe(809, 365, distance=600, responsedist=config.userconfigdict['RESPOND_Y'], horizontal=True)
            # 两次不同高度
            click((x_click[0], y_click[0]) if offset_lr==0 else (x_click[1], y_click[0]))
            click((x_click[0], y_click[1]) if offset_lr==0 else (x_click[1], y_click[1]))
            

            sleep(1)
            screenshot()
            # 尝试匹配右侧黄点篇章-大章节
            for ind, point_pos in enumerate(self.yellow_points):
                if match_pixel(point_pos, self.yellow_bgr):
                    logging.info({"zh_CN": f"检测到篇章{i}新章节{ind+1}，点击进入",
                                  "en_US": f"Detected eposide {i} New chapter {ind+1}, click to enter"})
                    self.run_until(
                        lambda: click((point_pos[0] + 10, point_pos[1] + 5)),
                        lambda: Page.is_page(PageName.PAGE_STORY_SELECT_SECTION),
                        sleeptime=1
                    )
                    # 尝试处理完当前黄点篇章所有可点的New小节
                    try_to_solve_new_section()
                    screenshot()
            # 全部章节都处理完了
            logging.info({"zh_CN": f"篇章下标{i}所有章节处理完毕", "en_US": f"Eposide index {i} All chapters have been processed"})

        # 处理最终篇
        logging.info({"zh_CN": "处理最终篇","en_US": "Process final"})
        logging.warn({"zh_CN": "最终篇涉及到走格子以及攻略战，暂不支持以上部分",
                      "en_US": "The final chapter involves grid walking and strategy battles, "
                               "which are not currently supported"})
        # 点击底部最终篇蓝色按钮
        click((846, 634))
        click((846, 634))
        sleep(2)
        screenshot()
        # 尝试匹配右侧黄点篇章-大章节
        for ind, point_pos in enumerate(self.yellow_points):
            if match_pixel(point_pos, self.yellow_bgr):
                logging.info({"zh_CN": f"检测到最终篇新章节{ind+1}，点击进入",
                              "en_US": f"Detect the final new chapter {ind+1}, click to enter"})
                self.run_until(
                    lambda: click((point_pos[0] + 10, point_pos[1] + 5)),
                    lambda: Page.is_page(PageName.PAGE_STORY_SELECT_SECTION),
                    sleeptime=1
                )
                # 尝试处理完当前黄点篇章所有可点的New小节
                try_to_solve_new_section()
                screenshot()
        logging.info({"zh_CN": f"最终篇所有章节处理完毕", "en_US": "All chapters of the final chapter have been processed"})

    def post_condition(self) -> bool:
        return self.back_to_home()