from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName
from modules.configs.MyConfig import config
from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
from modules.utils.log_utils import logging
from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, screenshot, match_pixel, get_screenshot_cv_data, compare_diff

class TouchHead(Task):
    # 安全的可点击边界，排除了下方按钮区域
    SAFE_X_LEFT = 110
    SAFE_X_RIGHT = 1279
    SAFE_Y_TOP = 130
    SAFE_Y_BOTTOM = 598
    def __init__(self, try_touch_epoch=3, name="TouchHead") -> None:
        super().__init__(name)
        self.try_touch_epoch = try_touch_epoch


    def pre_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_CAFE)

    def click_head_and_magic(self):
        # 清除可能的好感度弹窗
        click(Page.MAGICPOINT)
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_CAFE) and match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
        )
        canmatchRes = match(button_pic(ButtonName.BUTTON_STU_NOTICE), threshold=0.95, returnpos=True, rotate_trans=True)
        if canmatchRes[0]:
            logging.info({"zh_CN": "匹配到注意力符号，点击头部", "en_US": "match the 'mind' symbol, click it!"})
            # 中心点
            self.safe_click((canmatchRes[1][0]+50, canmatchRes[1][1]+30), sleeptime=0.1)
            # 四个角
            for offsetx in [-20, 20]:
                for offsety in [-30, 30]:
                    self.safe_click((canmatchRes[1][0]+50+offsetx, canmatchRes[1][1]+30+offsety), sleeptime=0.1)
            # 等待羁绊弹窗
            sleep(1)
        self.run_until(
            lambda: click(Page.MAGICPOINT),
            lambda: Page.is_page(PageName.PAGE_CAFE),
        )

    def safe_click(self, pos, sleeptime=1):
        x=pos[0]
        y=pos[1]
        if x<self.SAFE_X_LEFT or x>self.SAFE_X_RIGHT or y<self.SAFE_Y_TOP or y>self.SAFE_Y_BOTTOM:
            logging.warn({"zh_CN": f"点击坐标{pos}不在安全范围内，不点击", "en_US":f"Click position {pos} is not in the safe range"})
        else:
            click(pos, sleeptime=sleeptime)

    def swipeRight(self):
        swipe((1116, 129), (431, 129), 0.3)

    def swipeLeft(self):
        swipe((431, 129), (1116, 129), 0.3)

    def swipeDown(self):
        swipe((751, 420), (431, 129), 0.3)

    def swipeUp(self):
        swipe((431, 129), (751, 420), 0.3)

    def on_run(self) -> None:
        if config.userconfigdict["CAFE_CAMERA_FULL"]:
            if config.userconfigdict["CAFE_TOUCH_WAY_DIFF"]:
                # 如果使用了图片差异来摸头
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: Page.is_page(PageName.PAGE_CAFE) and match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                )
                # 左下进入编辑模式，截图
                click((68, 649), 1)
                screenshot()
                noStu = get_screenshot_cv_data()
                # 右上退出编辑模式
                click((1171, 95), 1)
                for match_times in range(int(2*self.try_touch_epoch)):
                    # 重复检测6+2次
                    # 确认来到咖啡厅页面
                    self.run_until(
                        lambda: click(Page.MAGICPOINT),
                        lambda: Page.is_page(PageName.PAGE_CAFE) and match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    )
                    logging.info({"zh_CN": "开始检测图片差异", "en_US": "Start detecting image discrepancies"})
                    if match_times != 0:
                        # 只是为了刷新学生们的位置，所以编辑模式内不需要再次截图
                        # 左下进入编辑模式
                        click((68, 649), 1)
                        # 右上退出编辑模式
                        click((1171, 95), 1)
                    # 获取有学生的截图
                    screenshot()
                    hasStu = get_screenshot_cv_data()
                    # 得出差异列表
                    diff_pos_list = compare_diff(noStu, hasStu, [1, 1279], [124, 568])
                    logging.info({"zh_CN": f"第{match_times+1}次检测到{len(diff_pos_list)}个差异中心",
                                  "en_US": f"{len(diff_pos_list)} centers of diff "
                                           f"were detected for the {match_times} time"})
                    # 挨个点击
                    for pos in diff_pos_list:
                        self.safe_click(pos, sleeptime=0.1)
                    sleep(1.5)
                # 最后用注意力符号模式再检查一下
                self.run_until(
                    lambda: self.click_head_and_magic(),
                    lambda: not match(button_pic(ButtonName.BUTTON_STU_NOTICE), threshold=0.95, rotate_trans=True),
                    times=3, # 直到找不到注意力符号
                    sleeptime=1
                )
            else:
                # 否则使用注意力符号来摸头
                # 视角最高直接点
                totalruns = self.try_touch_epoch
                times_in_run = 3
                for i in range(totalruns):
                    # sometimes a speak will cover the NOTICE icon, so we need to double check
                    click(Page.MAGICPOINT)
                    self.run_until(
                        lambda: self.click_head_and_magic(),
                        lambda: not match(button_pic(ButtonName.BUTTON_STU_NOTICE), threshold=0.95, rotate_trans=True),
                        times=times_in_run,  # 直到找不到注意力符号
                        sleeptime=1
                    )
                    logging.info({"zh_CN": f"第{i+1}/{totalruns}轮摸头结束",
                                  "en_US": f"Round{i+1}/{totalruns} petted is over"})
                    sleep(3)
        else:
            # 左右拖动换视角摸头
            TO_POS_LEFT = [self.swipeLeft, self.swipeLeft, self.swipeLeft]
            TO_POS_BOTTOM = [self.swipeDown, self.swipeDown, self.swipeDown]
            TO_POS_RIGHT = [self.swipeRight, self.swipeRight]
            TO_POS_RIGHT_SIDE = [self.swipeRight, self.swipeRight]
            TO_POS_CENTER = [self.swipeLeft, self.swipeUp, self.swipeUp, self.swipeUp]
            all_pos = [TO_POS_LEFT, TO_POS_BOTTOM, TO_POS_RIGHT, TO_POS_RIGHT_SIDE, TO_POS_CENTER]

            for movefuncs in all_pos:
                # 先摸再变视角
                # 这个画面里有多少次没有匹配到注意力符号
                times_not_match = 0
                for tt in range(8):
                    # 清除可能的好感度弹窗
                    self.run_until(
                        lambda: click(Page.MAGICPOINT),
                        lambda: Page.is_page(PageName.PAGE_CAFE) and match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                    )
                    screenshot()
                    if (match(button_pic(ButtonName.BUTTON_STU_NOTICE), threshold=0.95, rotate_trans=True)):
                        self.click_head_and_magic()
                    else:
                        # 失败次数超过3次就不再尝试
                        times_not_match += 1
                        if times_not_match == 3:
                            break
                # 变换视角前再次确认关闭弹窗回到咖啡厅页面
                self.run_until(
                    lambda: click(Page.MAGICPOINT),
                    lambda: Page.is_page(PageName.PAGE_CAFE) and match_pixel(Page.MAGICPOINT, Page.COLOR_WHITE),
                )
                logging.info({"zh_CN": "变换视角", "en_US": "Transform Perspective"})
                for func in movefuncs:
                    func()

    def post_condition(self) -> bool:
        return Page.is_page(PageName.PAGE_CAFE)