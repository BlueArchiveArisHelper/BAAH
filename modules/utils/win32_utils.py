from modules.utils.log_utils import logging, istr, CN, EN
import platform
if platform.system() != "Windows":
    mention_str = istr({
        CN: "win32_utils 只能在 Windows 系统上使用",
        EN: "win32_utils can only be used on Windows systems"
    })
    logging.error(mention_str)
    raise ImportError(mention_str)

import ctypes
# 尝试将进程设置为系统DPI感知
try:
    # 使用 SetProcessDpiAwareness 更现代的方法
    # 可选值: 0 (不感知), 1 (系统级感知), 2 (每显示器感知)
    awareness = ctypes.c_int(2) # 或 2 用于多显示器环境
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except Exception: # 如果失败（如旧版Windows），回退到旧API
    print("SetProcessDpiAwareness failed, trying SetProcessDPIAware")
    ctypes.windll.user32.SetProcessDPIAware()

# pywin32
import win32gui
import win32con
import win32api
import win32com
# pillow
from PIL import ImageGrab
import time
import numpy as np
import cv2
import pythoncom

def _get_hwnd(window_title):
    # 使用win32gui获取更精确的客户端区域
    hwnd = win32gui.FindWindow(None, window_title)
    return hwnd

def _get_dpi(window_title):
    # ((46, 35, 1280, 720), (38, 4, 1296, 759)) 100% 96DPI
    # ((57, 51, 1274, 703), (46, 6, 1296, 759)) 150% 144DPI
    try:
        screen_dpi = ctypes.windll.shcore.GetDpiForSystem()
    except:
        screen_dpi = ctypes.windll.user32.GetDpiForSystem()
    print(f"System DPI: {screen_dpi}")
    return screen_dpi

def check_esc_is_pressed():
    """
    检测Esc键是否被按下
    """
    # 使用win32api检测Esc键状态
    esc_state = win32api.GetAsyncKeyState(win32con.VK_ESCAPE)
    # 如果高位字节为1，表示按键被按下
    if esc_state & 0x8000:
        return True
    return False


def _get_window_client_pos(window_title):
    hwnd = _get_hwnd(window_title)
    cleft, ctop, cright, cbottom = win32gui.GetClientRect(hwnd)
    client_x, client_y = win32gui.ClientToScreen(hwnd, (cleft, ctop))
    window_x, window_y, gright, gbottom = win32gui.GetWindowRect(hwnd)
    client_width = cright - cleft
    client_height = cbottom - ctop
    window_width = gright - window_x
    window_height = gbottom - window_y
    # print(((client_x, client_y, client_width, client_height), (window_x, window_y, window_width, window_height)))
    # print(f"DPI: {_get_dpi(window_title)}")
    return  ((client_x, client_y, client_width, client_height), (window_x, window_y, window_width, window_height))

def _change_window_client_size(window_title):
    """将给定的窗口内的client区域设置为1280x720，返回设置是否成功"""
    hwnd = _get_hwnd(window_title)
    client_window_info = _get_window_client_pos(window_title)
    cx, cy, cw, ch = client_window_info[0]
    wx, wy, ww, wh = client_window_info[1]
    if cw!=1280 or ch!=720:
        # 计算宽度与高度和1280 720 差多少
        differ_width = 1280 - cw
        differ_height = 720 - ch
        # 现在窗口宽高
        target_window_width = ww + differ_width
        target_windo_height = wh + differ_height
        # 设置窗口大小（保持当前位置）
        win32gui.SetWindowPos(hwnd, 0, 0, 0, target_window_width, target_windo_height, 
                            win32con.SWP_NOMOVE | win32con.SWP_NOZORDER)
        
        time.sleep(1)

        client_window_info = _get_window_client_pos(window_title)
        cx, cy, cw, ch = client_window_info[0]
        if not cw or not ch:
            return False
    return cw == 1280 and ch == 720

def _wrap_activate_window(func):
    def wrapper(*args, **kwargs):
        # 窗口不存在的异常交由里层func处理
        try:
            window_title = "Blue Archive"
            hwnd = _get_hwnd(window_title)

            # 2. 恢复窗口（如果它被最小化）
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # print(f"窗口已恢复")
                logging.info(istr({
                    CN: "窗口已恢复",
                    EN: "Window is recover"
                }))
                time.sleep(0.5)
            
            foreground_hwnd = win32gui.GetForegroundWindow()
            if foreground_hwnd != hwnd:
                # 3. 将窗口设置为前景窗口（激活）
                pythoncom.CoInitialize()
                # win32gui.SetForegroundWindow(hwnd)
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)
                # print(f"窗口已激活")
                logging.info(istr({
                    CN: "窗口已激活",
                    EN: "Window is activate"
                }))
                time.sleep(0.5)
                pythoncom.CoUninitialize()
            
            # 设置1280*720
            client_window_info = _get_window_client_pos(window_title)
            cx, cy, cw, ch = client_window_info[0]
            if cw != 1280 or ch != 720:
                logging.info(istr({
                    CN: "调整分辨率为 1280*720",
                    EN: "Change resolution to 1280*720"
                }))
                _change_window_client_size(window_title)
        except Exception as e:
            print(f"wrap Exception: {str(e)}")
        result = func(*args, **kwargs)
        return result
    return wrapper


def _parse_normalized_coordinates(target_x, target_y):
    """给定全局坐标，转换为归一化全局坐标"""
    # 获取整个虚拟桌面的大小和左上角坐标
    # 注意：虚拟桌面的左上角坐标可能不是(0,0)，特别是在多显示器设置中，可能有负值区域[7](@ref)
    virtual_desktop_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    virtual_desktop_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    virtual_desktop_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    virtual_desktop_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    virtual_desktop_right = virtual_desktop_left + virtual_desktop_width
    virtual_desktop_bottom = virtual_desktop_top + virtual_desktop_height

    # print(f"虚拟桌面范围: 左上({virtual_desktop_left}, {virtual_desktop_top}), 右下({virtual_desktop_right}, {virtual_desktop_bottom})")

    # 计算归一化绝对坐标（范围0-65535）
    # 公式： normalized_x = (target_x - virtual_desktop_left) * 65535 / virtual_desktop_width[6,7](@ref)
    # 注意：确保目标坐标在虚拟桌面范围内
    if not (virtual_desktop_left <= target_x <= virtual_desktop_right and 
            virtual_desktop_top <= target_y <= virtual_desktop_bottom):
        raise ValueError(f"目标坐标({target_x}, {target_y})不在虚拟桌面范围内。")

    normalized_x = int((target_x - virtual_desktop_left) * 65535 / virtual_desktop_width)
    normalized_y = int((target_y - virtual_desktop_top) * 65535 / virtual_desktop_height)

    return normalized_x, normalized_y


def _click_in_multiple_screens(target_x, target_y):
    """
    在多显示器环境下，在指定的屏幕绝对坐标（像素）处执行鼠标左键点击。

    :param target_x: 目标点的x坐标（屏幕像素）
    :param target_y: 目标点的y坐标（屏幕像素）
    """
    normalized_x, normalized_y = _parse_normalized_coordinates(target_x, target_y)

    # 可选的标志，用于将坐标映射到整个虚拟桌面[7](@ref)
    # flags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK
    flags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK


    # 1. 首先将光标移动到目标位置（使用归一化坐标和包含虚拟桌面映射的标志）
    win32api.mouse_event(flags, normalized_x, normalized_y, 0, 0)

    # 2. 然后在该位置发送左键点击事件（注意：点击事件的坐标也需使用归一化坐标，或可省略，因为光标已就位）
    # 这里使用 MOUSEEVENTF_ABSOLUTE 标志，并确保坐标映射到虚拟桌面
    win32api.mouse_event(flags | win32con.MOUSEEVENTF_LEFTDOWN, normalized_x, normalized_y, 0, 0)
    win32api.mouse_event(flags | win32con.MOUSEEVENTF_LEFTUP, normalized_x, normalized_y, 0, 0)

def _scroll_in_multiple_screens(x1, y1, x2, y2, duration_ms):
    """
    在多显示器环境下，从指定的起始坐标滚动到目标坐标，持续时间为duration_ms毫秒。

    :param x1: 起始点的x坐标（屏幕像素）
    :param y1: 起始点的y坐标（屏幕像素）
    :param x2: 目标点的x坐标（屏幕像素）
    :param y2: 目标点的y坐标（屏幕像素）
    :param duration_ms: 滚动持续时间（毫秒）
    """
    normalized_x1, normalized_y1 = _parse_normalized_coordinates(x1, y1)
    normalized_x2, normalized_y2 = _parse_normalized_coordinates(x2, y2)

    steps = max(abs(normalized_x2 - normalized_x1), abs(normalized_y2 - normalized_y1)) // 200
    if steps == 0:
        steps = 1
    sleep_time_ms = duration_ms / steps

    # 1. 首先将光标移动到目标位置（使用归一化坐标和包含虚拟桌面映射的标志）
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK, normalized_x1, normalized_y1, 0, 0)

    # 按下鼠标左键
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_VIRTUALDESK | win32con.MOUSEEVENTF_LEFTDOWN, normalized_x1, normalized_y1, 0, 0)

    for step in range(steps + 1):
        intermediate_x = int(normalized_x1 + (normalized_x2 - normalized_x1) * step / steps)
        intermediate_y = int(normalized_y1 + (normalized_y2 - normalized_y1) * step / steps)
        win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK, intermediate_x, intermediate_y, 0, 0)
        time.sleep(sleep_time_ms / 1000.0)

    # 释放鼠标左键
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_VIRTUALDESK | win32con.MOUSEEVENTF_LEFTUP, normalized_x2, normalized_y2, 0, 0)

@_wrap_activate_window
def capture_program_window_precise():
    """
    精确截取程序窗口的客户端区域（不含标题栏和边框）
    """
    try:
        window_title = "Blue Archive"

        client_window_info = _get_window_client_pos(window_title)
        cx, cy, cw, ch = client_window_info[0]
        wx, wy, ww, wh = client_window_info[1]
        # 使用PIL的ImageGrab截取指定区域
        bbox = (cx, cy, cx + cw, cy + ch)
        screenshot = ImageGrab.grab(bbox)
        # print(screenshot.size)
        image_array = np.asarray(screenshot)
        # 将 RGB 转换为 OpenCV 默认的 BGR 格式以供 cv2 使用
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return image_array_bgr
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

@_wrap_activate_window
def click_program_window_precise(x, y):
    """
    点击clientWindow相对位置
    """
    if check_esc_is_pressed():
        raise KeyboardInterrupt("Esc key pressed, program terminated")
    try:
        window_title = "Blue Archive"
        client_window_info = _get_window_client_pos(window_title)
        cx, cy, cw, ch = client_window_info[0]
        # print(client_x, client_y)
        _click_in_multiple_screens(cx+x, cy+y)
    except Exception as e:
        print(str(e))

@_wrap_activate_window
def scroll_program_window_precise(x1, y1, x2, y2, duration_ms):
    if check_esc_is_pressed():
        raise KeyboardInterrupt("Esc key pressed, program terminated")
    try:
        window_title = "Blue Archive"
        client_window_info = _get_window_client_pos(window_title)
        cx, cy, cw, ch = client_window_info[0]
        _scroll_in_multiple_screens(cx+x1, cy+y1, cx+x2, cy+y2, duration_ms)
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    # click_program_window_precise(900, 600)
    scroll_program_window_precise(947, 537, 941, 275, 500)