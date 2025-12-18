from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task
import numpy as np

from modules.utils import click, get_screenshot_cv_data, match_pixel, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, find_color_diff_positions, logging, istr, CN, EN, screenshot


class ScrollSelect(Task):
    """
    滑动右侧窗口点击对应关卡

    Parameters
    ----------
    targetind : int
        目标关卡的下标，从0开始
    window_starty:
        窗口上边缘y坐标
    first_item_endy:
        第一个元素下边缘y坐标
    window_endy:
        窗口下边缘y坐标
    clickx: int
        滑动的基础x坐标，点击按钮的x坐标
    hasexpectimage: function
        期望点击后出现的图片判断函数，返回bool
    swipeoffsetx: int
        滑动时基础x坐标的x偏移量，防止滑动时意外点击按钮
    finalclick: bool
        是否滑动结束后点击clickx与y
    """

    def __init__(self, targetind, window_starty, first_item_endy, window_endy, clickx, hasexpectimage,
                 swipeoffsetx=-100, finalclick=True, name="ScrollSelect") -> None:
        # TODO: 其实只关心一个元素的高度，完全显示第一个按钮的y，完全显示贴底按钮的y,窗口容纳的完整的元素个数，最后一个元素在窗口里的那部分高度，以及向左偏移量和响应距离
        super().__init__(name)
        self.window_starty = window_starty
        self.first_item_endy = first_item_endy
        self.window_endy = window_endy
        self.targetind = targetind
        self.windowheight = window_endy - window_starty
        self.itemheight = first_item_endy - window_starty
        self.clickx = clickx
        self.hasexpectimage = hasexpectimage
        self.swipeoffsetx = swipeoffsetx
        if config.userconfigdict["RESPOND_Y"] is not None:
            self.responsey = config.userconfigdict['RESPOND_Y']
        else:
            logging.warn({"zh_CN": "未设置滑动触发距离RESPOND_Y，使用默认值40",
                          "en_US": "Default value 40 is used for swipe trigger distance RESPOND_Y"})
            self.responsey = 40
        self.finalclick = finalclick
        # 最后ScrollSelect任务想要点击的x,y坐标，当做出最终点击动作时，记录坐标到这个值
        self.wantclick_pos = [-1, -1]

    def pre_condition(self) -> bool:
        return True

    @staticmethod
    def compute_swipe(x1, y1, distance, responsedist, horizontal=False):
        """
        纵向从下向上/从右往左滑动，实际滑动距离根据两目标点距离distance计算，考虑惯性

        x1, y1: 
            起始点坐标
        distance: 
            要滑动的距离
        reponsedist: 
            滑动后，触发滑动响应的距离
        horizontal: bool
            是否横向滑动，默认为False
        """
        distance = abs(distance)
        logging.debug(f"滑动距离: {distance}")
        # 0-50
        if distance < 50:
            if horizontal:
                swipe((x1, y1), (x1 - (distance + responsedist), y1), 2)
            else:
                swipe((x1, y1), (x1, y1 - (distance + responsedist)), 2)
        else:
            if horizontal:
                swipe((x1, y1), (int(x1 - (distance + responsedist - 4 * (1 + distance / 100))), y1), 1 + distance / 100)
            else:
                swipe((x1, y1), (x1, int(y1 - (distance + responsedist - 4 * (1 + distance / 100)))), 1 + distance / 100)
            # swipe((x1, y1), (x1, y1-(200+40-4*3)), 3)
            # swipe((x1, y1), (x1, y1-(300+40-4*4)), 4)
            # swipe((x1, y1), (x1, y1-(400+40-4*5)), 5)

    def on_run(self) -> None:
        logging.info({"zh_CN": "滑动选取第{}个关卡".format(self.targetind+1),
                      "en_US": "Slide to select the {} level".format(self.targetind+1)})
        self.scroll_right_up(scrollx=self.clickx + self.swipeoffsetx)
        # 计算一个页面包含多少个完整的元素
        itemcount = self.windowheight // self.itemheight
        # 计算该页面最后那一个不完整的元素占了多高
        lastitemheight = self.windowheight % self.itemheight
        # 不完整的元素下方还有多少
        hiddenlastitemheight = self.itemheight - lastitemheight
        # 第一个元素高度中心点
        start_center_y = self.window_starty + self.itemheight // 2
        # 当页最后一个完整元素高度中心点
        end_center_y = start_center_y + (itemcount - 1) * self.itemheight
        # 如果目标元素就在当前页面
        if self.targetind < itemcount:
            # 目标元素高度中心点
            target_center_y = start_center_y + self.itemheight * self.targetind
            self.wantclick_pos = [self.clickx, target_center_y]
            if self.finalclick:
                self.run_until(
                    lambda: click((self.clickx, target_center_y)),
                    lambda: self.hasexpectimage(),
                )
        else:
            # 从关卡中间的空隙开始滑
            scroll_start_from_y = self.window_endy - self.itemheight // 2
            # 目标元素在之后的页面
            # 计算页面应该滑动多少
            scrolltotal_distance = (self.targetind - itemcount) * self.itemheight + hiddenlastitemheight
            logging.debug("最后一个元素隐藏高度: %d" % hiddenlastitemheight)
            # 先把hidden滑上来，多一点距离让ba响应这是个滑动事件
            self.compute_swipe(self.clickx + self.swipeoffsetx, scroll_start_from_y, hiddenlastitemheight,
                               self.responsey)
            logging.debug(f"滑动距离: {hiddenlastitemheight}")
            # 更新scrolltotal_distance
            scrolltotal_distance -= hiddenlastitemheight
            # 还需要往上滑(self.targetind - itemcount) * self.itemheight
            # 重要：每次先划itemcount-1个元素的高度
            if itemcount == 1:
                scroll_distance = itemcount * self.itemheight
            else:
                scroll_distance = (itemcount - 1) * self.itemheight
            while scroll_distance <= scrolltotal_distance:
                self.compute_swipe(self.clickx + self.swipeoffsetx, scroll_start_from_y, scroll_distance,
                                   self.responsey)
                scrolltotal_distance -= scroll_distance
            if scrolltotal_distance > 5:
                # 最后一次滑动
                self.compute_swipe(self.clickx + self.swipeoffsetx, scroll_start_from_y, scrolltotal_distance,
                                   self.responsey)
            self.wantclick_pos = [self.clickx, self.window_endy - self.itemheight // 2]
            if self.finalclick:
                # 点击最后一行
                self.run_until(
                    lambda: click((self.clickx, self.window_endy - self.itemheight // 2)),
                    self.hasexpectimage
                )

    def post_condition(self) -> bool:
        return True
    

class SmartScrollSelect(Task):
    """
    根据所给列进行边缘点分析，提取出按钮位置，分析每个按钮正中的坐标颜色，根据颜色筛选可点击的那些按钮
    
    可以用于找到已经解锁的最后一关，用于扫荡任务时注意已经解锁的最后一关可能并未3星可扫荡

    Parameters
    ----------
    targetind : int
        目标关卡的下标, 负数，一般是 -1 表示已经解锁的最后一个关卡
    window_starty:
        窗口上边缘y坐标 稍微超出窗口
    window_endy:
        窗口下边缘y坐标 稍微超出窗口
    clickx: int
        点击按钮的x坐标, 垂线需要经过关卡列表中的按钮以区分每个关卡的解锁状态
    active_button_color:
        已经解锁的关卡的颜色
    hasexpectimage: function
        期望点击后出现的图片判断函数，返回bool
    swipeoffsetx: int
        滑动时基础x坐标的x偏移量，防止滑动时意外点击按钮
    finalclick: bool
        是否滑动结束后点击clickx与y
    min_button_height: int
        关卡按钮的最小识别高度，默认40
    """
    def __init__(self, 
                    targetind, window_starty, window_endy, clickx, active_button_color, hasexpectimage,
                    swipeoffsetx=-100, finalclick=True, min_button_height=40,
                 name="SmartScrollSelect") -> None:
        super().__init__(name)
        self.targetind = targetind
        self.window_starty = int(window_starty)
        self.window_endy = int(window_endy)
        self.window_height = int(window_endy - window_starty)
        self.window_middley = int((window_starty + window_endy) / 2)
        self.clickx = clickx
        self.active_button_color = active_button_color
        self.hasexpectimage = hasexpectimage
        self.swipeoffsetx = swipeoffsetx
        self.finalclick = finalclick
        self.min_button_height = min_button_height

        # 最后ScrollSelect任务想要点击的x,y坐标，当做出最终点击动作时，记录坐标到这个值
        self.wantclick_pos = [-1, -1]

     
    def pre_condition(self) -> bool:
        return super().pre_condition()
    
    def go_down(self, swipe_during=0.5):
        """手指上划，下翻"""
        # 别从最边上滑动，这边从中间偏下方开始滑
        swipe((self.clickx+self.swipeoffsetx, self.window_middley + self.window_height//3), (self.clickx+self.swipeoffsetx, self.window_middley - self.window_height//3), durationtime=swipe_during)

    def go_up(self, swipe_during=0.5):
        """手指下划，上翻"""
        swipe((self.clickx+self.swipeoffsetx, self.window_middley - self.window_height//3), (self.clickx+self.swipeoffsetx, self.window_middley + self.window_height//3), durationtime=swipe_during)

    def analyze_column_segment(self):
        pixel_list = find_color_diff_positions((self.clickx, self.window_starty), distance=self.window_height, pic_data=get_screenshot_cv_data(), vertical=True)
        # 计算相邻两个点的高度差大于min_height的点对，也就是识别到的按钮坐标
        pair_list = SmartScrollSelect.compute_interval_greater_than(pixel_list, self.min_button_height)
        # 构造列表，分析每个按钮中间像素值，如果符合active_button_color，就认为是已经解锁的关卡
        enable_button_list = []
        for pair in pair_list:
            if match_pixel(pair[2], self.active_button_color):
                enable_button_list.append(pair[2])
        return enable_button_list
        
    @staticmethod
    def compute_interval_greater_than(pixel_list, min_height):
        """
        计算相邻两个点的高度差大于min_height的点对

        返回二维列表，元素为符合条件的 [start point, end point, middle point]
        """
        res_list = []
        for i in range(1, len(pixel_list)):
            last_p = pixel_list[i-1]
            this_p = pixel_list[i]
            distance = abs(last_p[1] - this_p[1]) + abs(last_p[0] - this_p[0])
            if distance > min_height:
                res_list.append((last_p, this_p, ((last_p[0] + this_p[0]) // 2, (last_p[1] + this_p[1]) // 2)))
        return res_list

    def on_run(self) -> None:
        # 基本逻辑就是先滑到底，然后识别，如果最后一个按钮已解锁，那最高关卡就是最后一个按钮
        # 不是的话就是找到已解锁与未解锁的分界，没找到就上划下
        for i in range(3):
            self.go_down()
        for try_times in range(3):
            screenshot()
            unlock_button_pixels = self.analyze_column_segment()
            # 如果没有找到解锁的按钮或解锁的按钮数量不够，就继续上划
            if len(unlock_button_pixels) < abs(self.targetind):
                self.go_up(swipe_during=2)
                sleep(1)
            else:
                break
        # 有足够的按钮数量，点击
        if len(unlock_button_pixels) >= abs(self.targetind):
            logging.info(istr({
                CN: f"找到解锁的按钮坐标: {unlock_button_pixels}",
                EN: f"Found the coordinates of the unlocked button: {unlock_button_pixels}"
            }))
            self.wantclick_pos = [self.clickx, unlock_button_pixels[self.targetind][1]]
            if self.finalclick:
                self.run_until(
                    lambda: click(self.wantclick_pos),
                    self.hasexpectimage
                )
        else:
            logging.warn({"zh_CN": "没有找到解锁的按钮",
                          "en_US": "No unlocked button found"})
            return False
        
        

     
    def post_condition(self) -> bool:
        return super().post_condition()