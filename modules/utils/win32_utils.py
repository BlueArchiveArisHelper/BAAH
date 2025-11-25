# pywin32
import win32gui
import win32con
import win32api
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

def _wrap_activate_window(func):
    def wrapper(*args, **kwargs):
        window_title = "Blue Archive"
        hwnd = _get_hwnd(window_title)

        # 2. 恢复窗口（如果它被最小化）
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            print(f"窗口已恢复")
            time.sleep(0.5)
        
        foreground_hwnd = win32gui.GetForegroundWindow()
        if foreground_hwnd != hwnd:
            # 3. 将窗口设置为前景窗口（激活）
            pythoncom.CoInitialize()
            win32gui.SetForegroundWindow(hwnd)
            print(f"窗口已激活")
            time.sleep(0.5)
            pythoncom.CoUninitialize()
        result = func(*args, **kwargs)
        return result
    return wrapper

def _get_window_client_pos(window_title):
    hwnd = _get_hwnd(window_title)
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    client_x, client_y = win32gui.ClientToScreen(hwnd, (left, top))
    client_width = right - left
    client_height = bottom - top
    return  client_x, client_y, client_width, client_height

@_wrap_activate_window
def capture_program_window_precise():
    """
    精确截取程序窗口的客户端区域（不含标题栏和边框）
    """
    try:
        window_title = "Blue Archive"

        client_x, client_y, client_width, client_height = _get_window_client_pos(window_title)
        # 使用PIL的ImageGrab截取指定区域
        bbox = (client_x, client_y, client_x + client_width, client_y + client_height)
        screenshot = ImageGrab.grab(bbox)
        print(screenshot.size)
        image_array = np.asarray(screenshot)
        # 将 RGB 转换为 OpenCV 默认的 BGR 格式以供 cv2 使用
        image_array_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return image_array_bgr
        
    except Exception as e:
        print(f"错误: {str(e)}")

def _click_in_multiple_screens(target_x, target_y):
    """
    在多显示器环境下，在指定的屏幕绝对坐标（像素）处执行鼠标左键点击。

    :param target_x: 目标点的x坐标（屏幕像素）
    :param target_y: 目标点的y坐标（屏幕像素）
    """
    # 获取整个虚拟桌面的大小和左上角坐标
    # 注意：虚拟桌面的左上角坐标可能不是(0,0)，特别是在多显示器设置中，可能有负值区域[7](@ref)
    virtual_desktop_left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    virtual_desktop_top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    virtual_desktop_width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    virtual_desktop_height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    virtual_desktop_right = virtual_desktop_left + virtual_desktop_width
    virtual_desktop_bottom = virtual_desktop_top + virtual_desktop_height

    print(f"虚拟桌面范围: 左上({virtual_desktop_left}, {virtual_desktop_top}), 右下({virtual_desktop_right}, {virtual_desktop_bottom})")

    # 计算归一化绝对坐标（范围0-65535）
    # 公式： normalized_x = (target_x - virtual_desktop_left) * 65535 / virtual_desktop_width[6,7](@ref)
    # 注意：确保目标坐标在虚拟桌面范围内
    if not (virtual_desktop_left <= target_x <= virtual_desktop_right and 
            virtual_desktop_top <= target_y <= virtual_desktop_bottom):
        raise ValueError(f"目标坐标({target_x}, {target_y})不在虚拟桌面范围内。")

    normalized_x = int((target_x - virtual_desktop_left) * 65535 / virtual_desktop_width)
    normalized_y = int((target_y - virtual_desktop_top) * 65535 / virtual_desktop_height)

    # 可选的标志，用于将坐标映射到整个虚拟桌面[7](@ref)
    # flags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK
    flags = win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_VIRTUALDESK


    # 1. 首先将光标移动到目标位置（使用归一化坐标和包含虚拟桌面映射的标志）
    win32api.mouse_event(flags, normalized_x, normalized_y, 0, 0)

    # 2. 然后在该位置发送左键点击事件（注意：点击事件的坐标也需使用归一化坐标，或可省略，因为光标已就位）
    # 这里使用 MOUSEEVENTF_ABSOLUTE 标志，并确保坐标映射到虚拟桌面
    win32api.mouse_event(flags | win32con.MOUSEEVENTF_LEFTDOWN, normalized_x, normalized_y, 0, 0)
    win32api.mouse_event(flags | win32con.MOUSEEVENTF_LEFTUP, normalized_x, normalized_y, 0, 0)

@_wrap_activate_window
def click_program_window_precise(x, y):
    """
    点击clientWindow相对位置
    """
    window_title = "Blue Archive"
    client_x, client_y, client_width, client_height = _get_window_client_pos(window_title)
    print(client_x, client_y)
    _click_in_multiple_screens(client_x+x, client_y+y)

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

if __name__ == "__main__":
    click_program_window_precise(900, 600)