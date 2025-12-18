from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.InTimeTable.SmartSelect import SmartSelect
from modules.AllTask.Task import Task
from modules.configs.MyConfig import config

from modules.utils import (click, screenshot, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area_0,
                           ocr_area, get_screenshot_cv_data, match_pixel)
from modules.utils.log_utils import logging
from .LocationSelect import LocationSelect


class InTimeTable(Task):
    def __init__(self, name="InTimeTable") -> None:
        super().__init__(name)

    def pre_condition(self) -> bool:
        return self.back_to_home()

    def on_run(self) -> None:
        self.run_until(
            lambda: click((212, 669)),
            lambda: Page.is_page(PageName.PAGE_TIMETABLE)
        )

        if not config.sessiondict["TIMETABLE_NO_TICKET"] and config.userconfigdict["SMART_TIMETABLE"]:
            # 如果有票卷且用户开启了智能选择
            SmartSelect().run()
        else:
            # for each TIMETABLE_TASK, determine whether you need to click in
            for i in range(len(config.userconfigdict['TIMETABLE_TASK'])):
                if config.sessiondict["TIMETABLE_NO_TICKET"]:
                    logging.info({"zh_CN": "课程表/时间表 无票卷， 退出此任务",
                                  "en_US": "Schedule/Time Sheet No Ticket, exit this task"})
                    break
                # 如果这一location没有任务，就不点进去
                if len(config.userconfigdict['TIMETABLE_TASK'][i]) == 0:
                    continue
                LocationSelect(location=i, classrooms=config.userconfigdict['TIMETABLE_TASK'][i]).run()
        self.back_to_home()

    def post_condition(self) -> bool:
        return self.back_to_home()