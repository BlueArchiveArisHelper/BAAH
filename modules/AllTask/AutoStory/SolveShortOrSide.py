
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP, get_screenshot_cv_data, get_similarity
from modules.utils.log_utils import logging

from modules.AllTask.AutoStory.StoryHelper import try_to_solve_new_section, goto_story_page


class SolveShortOrSide(Task):
    """
    type = "short" | "side"

    短篇剧情 | 支线剧情
    """
    def __init__(self, type, name="SolveShortOrSide") -> None:
        super().__init__(name)
        self.type = type
        self.focus_page_area = ([133, 184], [346, 283])
        """判断页面翻页是否有变化的区域，用于判断是否停止翻页，左上角第一张图片的两个点"""

     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    def get_first_pic_data(self):
        this_page_data = get_screenshot_cv_data()
        if this_page_data is None:
            return None
        fist_pic_data = this_page_data[self.focus_page_area[0][1]:self.focus_page_area[1][1], self.focus_page_area[0][0]:self.focus_page_area[1][0]]
        return fist_pic_data
     
    def on_run(self) -> None:
        goto_story_page()
        # 进入短篇剧情 | 支线剧情
        if self.type == "short":
            click_pos = [732, 263]
        else:
            click_pos = [1021, 265]
        self.clear_popup()
        click(click_pos, sleeptime = 2)
        self.clear_popup()
        # 向左翻到底
        for _ in range(8):
            click([40, 357])
        # 进入短篇剧情 | 支线剧情 页面后，尝试解决新的New小节，并向右翻页
        # 记录第一个格子的像素内容以判断是否翻页有效
        while(True):
            # 记录第一张图片
            self.clear_popup()
            first_pic = self.get_first_pic_data()
            if first_pic is None:
                logging.warn(istr({
                    CN: "无法获取当前页面的像素数据，停止",
                    EN: "Unable to get pixel data of current page, stop"
                }))
                break
            # =========处理当前页面新剧情=======
            for _ in range(6):
                # 匹配new，点击
                match_res = match(button_pic(ButtonName.BUTTON_NEW_STORY_LEVEL), threshold=0.7, returnpos=True)
                if not match_res[0]:
                    logging.info(istr({
                        CN: "本页无New剧情，停止",
                        EN: "No new story in this page, stop"
                    }))
                    break
                # 进入New剧情小节选择页面，页面右侧为 “章节目录” 列表
                goinside = self.run_until(
                    lambda: click([match_res[1][0] + 50, match_res[1][1] + 30]),
                    lambda: Page.is_page(PageName.PAGE_STORY_SELECT_SECTION),
                    times = 4
                )
                if goinside:
                    logging.info(istr({
                        CN: "处理New剧情中",
                        EN: "Processing new story"
                    }))
                    try_to_solve_new_section(new_button_threshold=0.8)

            # ================================

            # 翻页
            self.clear_popup()
            click([1253, 359], sleeptime = 1)
            self.clear_popup()
            next_page_fist_pic = self.get_first_pic_data()
            # 比较翻页前后的第一张图片，判断是否翻页成功
            similarity = get_similarity(first_pic, next_page_fist_pic)
            if similarity > 0.9:
                logging.info(istr({
                    CN: f"翻页停止: {similarity}",
                    EN: f"Stop flipping: {similarity}"
                }))
                break
            else:
                logging.info(istr({
                    CN: f"翻页成功: {similarity}",
                    EN: f"Flip success: {similarity}"
                }))



     
    def post_condition(self) -> bool:
        return self.back_to_home()