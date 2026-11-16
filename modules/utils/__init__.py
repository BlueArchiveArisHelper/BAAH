# 针对于单个BAAH任务实例的工具方法，默认截图内容为当前BAAH任务实例的模拟器截图
import json
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName
from typing import Tuple, Union
from .adb_utils import *
from .image_processing import *
from .subprocess_helper import *
from .grid_analyze import *
from .notification import *
from .data_utils import *
from .I18nstr import *
from .baah_exceptions import *
from .adb_utils import _is_PC_app, _is_STEAM_app
from .screen_geometry import is_169ratio, is_720p, is_horizontal_screen

from modules.utils.log_utils import logging
import time
from modules.configs.MyConfig import config, ActionType
from modules.configs.multiserverSettings import MultiServerType, is_server_type_in_group, get_correct_asset, AssetMappingKeys

def get_config_time_after_click(use_config = None):
    if use_config is None:
        use_config = config
    return use_config.userconfigdict['TIME_AFTER_CLICK']

def get_config_screenshot_name(use_config = None):
    if use_config is None:
        use_config = config
    return use_config.userconfigdict['SCREENSHOT_NAME']

def get_config_pic_path(use_config = None):
    if use_config is None:
        use_config = config
    return use_config.userconfigdict['PIC_PATH']

def get_screenshot_cv_data():
    """
    获取截图的内容数据，当图片截图出错时，返回的内容是None
    """
    if config.userconfigdict["SCREENSHOT_METHOD"] == "pipe":
        return config.sessiondict["SCREENSHOT_DATA"]
    else:
        try:
            return cv2.imread(get_config_screenshot_name())
        except Exception as e: 
            logging.error(istr({
                CN: f"读取图片文件出错，{e}",
                EN: f"Error when reading pic file, {e}"
            }))
            return None

def click(item:Union[str, Tuple[float, float]], sleeptime = -1, threshold=0.87) -> bool:
    """
    Task: click the position (x, y) or the center of a picture (given by a str)
    
    This action will sleep for a while after click
    """
    # check if the item is a str
    if isinstance(item, str):
        matchRes = match(item, returnpos=True, threshold=threshold)
        if matchRes[0]:
            click_on_screen(matchRes[1][0], matchRes[1][1])
            if(sleeptime!=-1):
                time.sleep(sleeptime)
            else:
                time.sleep(get_config_time_after_click())
            return True
        else:
            logging.warning({"zh_CN": "无法匹配模板图像: {} ".format(item), "en_US":"Cannot match the pattern: {} ".format(item)})
            return False
    else:
        click_on_screen(item[0], item[1])
        if(sleeptime!=-1):
            time.sleep(sleeptime)
        else:
            time.sleep(get_config_time_after_click())
        return True

def swipe(item:Union[str, Tuple[float, float]], toitem: Union[str, Tuple[float, float]], durationtime = 0.3, sleeptime = -1) -> bool:
    """
    Task: swipe the position (x, y) or the center of a picture to a position or a picture
    
    time: seconds
    """
    frompos = None
    topos = None
    # check if the item is a str
    if isinstance(item, str):
        (res, pos) = match_pattern(sourcepic_mat=get_screenshot_cv_data() ,patternpic=item)
        if res:
            frompos = (pos[0], pos[1])
    else:
        frompos = (item[0], item[1])
    if isinstance(toitem, str):
        (res, pos) = match_pattern(sourcepic_mat=get_screenshot_cv_data(), patternpic=toitem)
        if res:
            topos = (pos[0], pos[1])
    else:
        topos = (toitem[0], toitem[1])
    if(frompos and topos):
        swipe_on_screen(frompos[0], frompos[1], topos[0], topos[1], durationtime*1000)
        if sleeptime == -1:
            sleep(get_config_time_after_click())
        else:
            sleep(sleeptime)
        return True
    else:
        logging.warning("Cannot find the target pattern {} and {} when try to swipe".format(item, toitem))
        return False

def match(imgurl:str, threshold:float = 0.87, returnpos = False, rotate_trans=False) -> bool | Tuple[bool, Tuple[float, float], float]:
    """
    Task: given a pattern picture url match it
    
    match result will only differ a little if there just have a light change
    
    if returnpos is True,
        return [whether the pattern is found, (x of the pattern, y of the pattern), the max matching val]
    else:
        return boolean
        
    if rotate_trans is True, the pattern will be rotated if it is transparent
    """
    # check if the item is a str
    if returnpos:
        return match_pattern(get_screenshot_cv_data(),imgurl, threshold=threshold, auto_rotate_if_trans=rotate_trans)
    else:
        return match_pattern(get_screenshot_cv_data(),imgurl, threshold=threshold, auto_rotate_if_trans=rotate_trans)[0]

def ocr_area(frompixel, topixel, multi_lines = False, ocr_lang = OCR_LANG.EN) -> Tuple[str, float]:
    """
    OCR the area in the given rectangle area of screenshot
    
    frompixel: (x, y)
    topixel: (x, y)
    
    axis is in image form, x axis is the horizontal axis, y axis is the vertical axis
    """
    lowerpixel = (min(frompixel[0], topixel[0]), min(frompixel[1], topixel[1]))
    highterpixel = (max(frompixel[0], topixel[0]), max(frompixel[1], topixel[1]))
    ocr_result = ocr_pic_area(get_screenshot_cv_data(), lowerpixel[0], lowerpixel[1], highterpixel[0], highterpixel[1], multi_lines=multi_lines, ocr_lang = ocr_lang)
    return ocr_result

def ocr_area_0(frompixel, topixel, ocr_lang = OCR_LANG.EN) -> bool:
    """
    OCR the number in the given rectangle area whether it is 0, return False if length>1
    
    frompixel: (x, y)
    topixel: (x, y)
    
    axis is in image form, x axis is the horizontal axis, y axis is the vertical axis
    """
    lowerpixel = (min(frompixel[0], topixel[0]), min(frompixel[1], topixel[1]))
    highterpixel = (max(frompixel[0], topixel[0]), max(frompixel[1], topixel[1]))
    res_str = ocr_pic_area(get_screenshot_cv_data(), lowerpixel[0], lowerpixel[1], highterpixel[0], highterpixel[1], ocr_lang = ocr_lang)[0]
    res_str = res_str.strip()
    allpossibles = ["0", "O", "o", "Q", "０"]
    # 如果长度为1，就判断它是不是0
    if len(res_str) == 1:
        if res_str[0] in allpossibles:
            return True
    # # 一长串判断是否有0，必须得是第一个字符或者前面没有数字
    # if len(res_str) >= 2:
    #     if res_str[0] in allpossibles:
    #         return True
    #     for i in range(1, len(res_str)):
    #         if res_str[i] in allpossibles and not res_str[i-1].isdigit():
    #             return True
    # 长度大于1直接返回False
    return False

def get_pixel(xy):
    """
        get the pixel color at the given position
        
        axis is in image form
    """
    sc_mat_data = get_screenshot_cv_data()
    return sc_mat_data[int(xy[1]), int(xy[0])][:3] if sc_mat_data is not None else [-1, -1, -1]

def match_pixel(xy, color, printit = False):
    """
        match whether the pixel is the given color
        
        color: Page.COLOR_*
        axis is in image form
    """
    sc_mat_data = get_screenshot_cv_data()
    return match_pixel_color_range(sc_mat_data, xy[0], xy[1], color[0], color[1], printit=printit)

def page_pic(picname, use_config = None):
    """
    给定页面的图片名称，得到图片的路径
    """
    # get_config_pic_path() + "/PAGE" + f"/{picname}.png"
    return os.path.join(get_config_pic_path(use_config), "PAGE", f"{picname}.png")

def button_pic(buttonname, use_config = None):
    """
    给定按钮的图片名称，得到图片的路径
    """
    # get_config_pic_path() + "/BUTTON" + f"/{buttonname}.png"
    return os.path.join(get_config_pic_path(use_config), "BUTTON", f"{buttonname}.png")

def popup_pic(popupname, use_config = None):
    """
    给定弹窗的图片名称，得到图片的路径
    """
    # get_config_pic_path() + "/POPUP" + f"/{popupname}.png"
    return os.path.join(get_config_pic_path(use_config), "POPUP", f"{popupname}.png")

def get_grid_solution_json(location, level, ishard=False):
    # 读取DATA/grid_config/quest/里的文件
    ishardstr = "h" if ishard else ""
    filename = f"./DATA/grid_solution/quest/{ishardstr}{location}-{level}.json"
    # 读取并解析json返回
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def sleep(seconds:float):
    """
    Task: sleep for seconds
    """
    time.sleep(seconds)
    
def _update_history_screenshot_list():
    """
    更新历史截图列表，最多保存4张截图
    """
    history_list = config.sessiondict["HISTORY_SCREENSHOT_LIST"]
    sc_data = get_screenshot_cv_data()
    if sc_data is not None:
        history_list.append(sc_data)
        if len(history_list) > 4:
            history_list.pop(0)
    config.sessiondict["HISTORY_SCREENSHOT_LIST"] = history_list

def screenshot(output_png = False):
    """
    Task: take a screenshot

    Params
    ------
    output_png:
        是否强制保存到png图片
    """
    # start = time.time()
    screen_shot_to_global(output_png = output_png)
    _global_screenshot_check()
    _update_history_screenshot_list()
    # end = time.time()
    # 输出截图耗时小数点后两位
    # logging.debug("截图耗时{:.2f}秒".format(end-start))
    
def check_connect():
    # 检查当前python目录下是否有screenshot.png文件，如果有就删除
    if os.path.exists(get_config_screenshot_name()):
        logging.info({"zh_CN": f"删除{get_config_screenshot_name()}", "en_US":f"Delete {get_config_screenshot_name()}"})
        os.remove(get_config_screenshot_name())
    connect_to_device()
    reconnect_offline()
    # PC端尝试调整ba窗口大小为720p
    if is_server_type_in_group(config, MultiServerType.PCGroup) and platform.system() == "Windows":
        from .win32_utils import _change_window_client_size
        window_title = config.userconfigdict["ACTIVITY_PATH"].split("/")[0]
        _change_window_client_size(window_title)
    # 尝试截图
    screenshot()
    time.sleep(1)
    sc_data = get_screenshot_cv_data()
    # 各步骤检查结果
    check_size_scale = False # 分辨率比例
    check_dpi = False # dpi
    # 提醒信息list
    mention_list = []
    if sc_data is not None:
        mention_list.append(istr({
            CN: "截图成功",
            EN: "Screenshot success"
        }))
        # 检查图片长和宽
        native_width = config.sessiondict.get("NATIVE_SCREENSHOT_WIDTH")
        native_height = config.sessiondict.get("NATIVE_SCREENSHOT_HEIGHT")
        wm_width, wm_height = native_width, native_height # 兼容老代码
        # 是否开启了16：9兼容模式
        compatibility_169 = config.userconfigdict["ENABLE_169_COMPATIBILITY_MODE"]
        # 检查分辨率和比例要求
        if compatibility_169:
            check_size_scale = is_169ratio(wm_width, wm_height, rotate_free=True)
        else:
            check_size_scale = is_720p(wm_width, wm_height, rotate_free=True)
        if not check_size_scale:
            mention_list.append(istr({
                CN: f'{"已开启" if compatibility_169 else "未开启"} 16:9 兼容模式，要求宽高1280x720, 当前宽高 {wm_width}x{wm_height}, 不符合要求。{"请设置16:9画面" if compatibility_169 else "请设置 1280x720 画面"}',
                EN: f'{"Enable" if compatibility_169 else "Disable"} 16:9 compatibility mode, required size 1280x720, current size {wm_width}x{wm_height}, not align with requirement. {"Please set 16:9 screen." if compatibility_169 else "Please set 1280x720 screen."}'
            }))
        # 检查dpi要求
        if "240" not in get_dpi():
            mention_list.append(istr({
                CN: f"目标DPI为240，当前DPI为{get_dpi()}",
                EN: f"Target DPI is 240, current dpi is {get_dpi()}"
            }))
        set_dpi(240) # 强制设置dpi为240，避免截图异常
        check_dpi = "240" in get_dpi()
    else:
        # 截图文件为空
        mention_list.append(istr({
            CN: f"截图文件为空",
            EN: "Screenshot is null"
        }))
        if is_server_type_in_group(config, MultiServerType.PCGroup):
            mention_list.append(istr({
                CN: f"请以管理员身份运行BAAH，检查游戏是否在更新，或检查PC端ba程序是否正常运行",
                EN: f"Please run BAAH as admin, and check if the game is updating or if the PC ba program is running normally"
            }))
        else:
            mention_list.append(istr({
                CN: f"请检查模拟器是否正常运行，或检查模拟器adb连接端口号是否正确",
                EN: f"Please check if the emulator is running normally, or check if the emulator adb connection port number is correct"
            }))
            if "127.0.0.1" in getNewestSeialNumber():
                mention_list.append(istr({
                    CN: "请确保关闭模拟器网络桥接", 
                    EN: "Please check if the emulator network bridging is turned off"
                }))
            # adb devices
            all_devices_list = get_all_devices()
            mention_list.append(istr({
                CN: f"连接方式 ({getNewestSeialNumber()})是否正确? 当前检测到的设备列表:",
                EN: f"Is Connection ({getNewestSeialNumber()}) right?Detected devices:"
            }))
            for each in all_devices_list:
                mention_list.append(f"    {each}")
    # ---------- return ----------
    for line in mention_list:
        logging.info(line)
    return check_size_scale and check_dpi

def _global_screenshot_check():
    """
    全局的截图元素检查，是否有卡顿弹窗等
    """
    if "NGS" in ocr_area([444, 307], [829, 355])[0] and match(popup_pic(PopupName.POPUP_NOTICE)):
        raise EmulatorBlockError(istr({
            CN: "匹配到NGS，触发模拟器卡顿异常",
            EN: "Match NGS, trigger emulator lag error"
        }))
    if match(button_pic(ButtonName.BUTTON_RECONNECT)):
        click(button_pic(ButtonName.BUTTON_RECONNECT))
        logging.warn(istr({
            CN: "检测到网络异常弹窗，点击重连按钮",
            EN: "Network exception popup detected, reconnect button clicked"
        }))

def logic_run_until(func1, func2, times=None, sleeptime = None) -> bool:
    """
    重复执行func1，至多times次或直到func2成立
    
    func1内部应当只产生有效操作一次或内部调用截图函数, func2判断前会先触发截图
    
    每次执行完func1后,等待sleeptime秒

    如果func2成立退出，返回true，否则返回false
    """
    # 设置times，如果传进来是None，就用config里的值
    if(times == None):
        times = config.userconfigdict["RUN_UNTIL_TRY_TIMES"]
    # 设置sleeptime，如果传进来是None，就用config里的值
    if(sleeptime == None):
        sleeptime = config.userconfigdict["RUN_UNTIL_WAIT_TIME"]
    for i in range(times):
        screenshot()
        if(func2()):
            return True
        func1()
        sleep(sleeptime)
    screenshot()
    if(func2()):
        return True
    logging.warning("run_until exceeded max times")
    return False

def _get_edition():
    """
    获取发行版本，返回"linux-container"（容器版） "windows-pyinstaller"（PyInstaller版） "linux-other"（其他Linux版） "windows-other"（其他Windows版） "other"（其他未知版本）
    """
    import platform
    import os
    if platform.system() == "Linux":
        if os.environ.get("BAAH_EDITION") == "container":
            return "linux-container"
        else:
            return "linux-other"
    elif platform.system() == "Windows":
        if os.path.exists("BAAH.exe"):
            return "windows-pyinstaller"
        else:
            return "windows-other"
    else:
        return "other"
