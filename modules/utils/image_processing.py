import cv2
from cv2.typing import MatLike
from modules.utils.log_utils import logging
import math
from modules.configs.MyConfig import config
import numpy as np
from typing import Tuple
from pponnxcr import TextSystem
import time
from os.path import exists
from math import isnan
from enum import Enum
import os

OCR_SYS_EN = TextSystem('en')
OCR_SYS_ZHT = TextSystem('zht')
OCR_SYS_ZHS = TextSystem('zhs')

class OCR_LANG(Enum):
    """
    用于选择ocr所用的语言
    """
    EN = 1
    ZHT = 2
    ZHS = 3

def get_similarity(img1, img2):
    """img1: MatLike, img2: MatLike"""
    similar = np.sum(np.minimum(img1, img2)) / np.sum(np.maximum(img1, img2))
    return similar


def rotate_image_with_transparency(image_mat, angle):
    """
    给定一个包含透明层的图像Mat，将其旋转angle角度，返回旋转后的图像Mat

    """
    # 获取到图像的对角线长度
    diagonal = int(math.sqrt(pow(image_mat.shape[0], 2) + pow(image_mat.shape[1], 2)))
    # 创建一个diagonal * diagonal的空白含透明度的图像Mat
    rotated_image = np.zeros((diagonal, diagonal, 4), dtype=np.uint8)
    # 将原图像复制到新图像的中心
    x_offset = (diagonal - image_mat.shape[1]) // 2
    y_offset = (diagonal - image_mat.shape[0]) // 2
    rotated_image[y_offset:y_offset+image_mat.shape[0], x_offset:x_offset+image_mat.shape[1]] = image_mat
    # 获取rotated_image的高度、宽度和中心点
    center = (diagonal // 2, diagonal // 2)

    # 定义旋转矩阵
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    # 执行旋转，多出来的部分全透明
    rotated_image = cv2.warpAffine(rotated_image, rotation_matrix, (diagonal, diagonal), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
    # 返回中心和原图一样大小的区域
    return rotated_image[y_offset:y_offset+image_mat.shape[0], x_offset:x_offset+image_mat.shape[1]]


def check_the_pic_validity(_img, _templ):
    """
    检查图片和模板的维度色深是否一致，返回是否有效
    
    (depth == CV_8U || depth == CV_32F) && type == _templ.type() && _img.dims() <= 2
    """
    # int type = _img.type(), depth = CV_MAT_DEPTH(type), cn = CV_MAT_CN(type);
    valid = True
    if _img is None or _templ is None:
        valid = False
    else:
        if isinstance(_img, np.ndarray):
            # numpy ndarray类型
            depth = _img.dtype
        else:
            # cv2 MatLike类型
            depth = _img.type().depth()
        if (depth == cv2.CV_8U or depth == cv2.CV_32F) and _img.type() == _templ.type() and _img.dims() <= 2:
            valid = False
    if not valid:
        logging.warn({"zh_CN": "图像匹配出错：", "en_US":"Error in image matching:"})
        if _img is None or _templ is None:
            logging.warn({"zh_CN": "图片为空", "en_US":"Picture is null"}) if _img is None else logging.warn({"zh_CN": "模板为空", "en_US":"Pattern is null"})
        else:
            logging.warn(f"Pic type: {_img.type()}, Pattern type: {_templ.type()}")
            logging.warn(f"Pic dims: {_img.dims()} <=2 : {_img.dims()<2}")
        config.sessiondict["SCREENSHOT_READ_FAIL_TIMES"] += 1
        if config.sessiondict["SCREENSHOT_READ_FAIL_TIMES"] > 5:
            logging.error({"zh_CN": "读取截图文件失败次数过多，退出程序", "en_US":"The number of failed attempts to read the screenshot file is too many, exit the program"})
            raise Exception("由于卡顿或其他原因，截图文件损坏过多次，请尝试清理电脑内存后重启程序")
        return False
    return True

def match_pattern(sourcepic_mat: MatLike, patternpic: str|MatLike,threshold: float = 0.9, show_result:bool = False, auto_rotate_if_trans = False) -> Tuple[bool, Tuple[float, float], float]:
    """
    Match the pattern picture in the source picture.
    
    If the pattern picture is a transparent picture, it will be rotated to match the source picture.

    Params
    ------
    sourcepic_mat: Big pictures which may contains pattern, in MatLike
    patternpic: Small pattern picture path to be matched, in str
    """
    # logging.debug("Matching pattern {}".format(patternpic))
    default_response = (False, (0, 0), 0)
    try:
        screenshot_cvmat = sourcepic_mat
        assert screenshot_cvmat is not None
    except:
        logging.error({"zh_CN": "无法读取截图文件", "en_US":"Cannot read the screenshot file"})
        config.sessiondict["SCREENSHOT_READ_FAIL_TIMES"] += 1
        if config.sessiondict["SCREENSHOT_READ_FAIL_TIMES"] > 5:
            logging.error({"zh_CN": "读取截图文件失败次数过多，退出程序", "en_US":"The number of failed attempts to read the screenshot file is too many, exit the program"})
            raise Exception("由于卡顿或其他原因，截图文件损坏，请尝试清理电脑内存后重启程序")
        return default_response
    if isinstance(patternpic, str):
        # 检查图片是否存在
        if not exists(patternpic):
            logging.error({"zh_CN": "匹配的模板图片 文件不存在: {}".format(patternpic), "en_US":"The pattern picture file does not exist: {}".format(patternpic)})
            return default_response
        pattern = cv2.imread(patternpic, cv2.IMREAD_UNCHANGED)  # 读取包含透明通道的模板图像
    else:
        # MatLike类型直接赋值给pattern
        pattern = patternpic
        if pattern is None:
            logging.error({
                "zh_CN": "匹配的模板图片为空", 
                "en_US":"The pattern picture is None"
            })
            return default_response
    # 判断透明度通道
    have_alpha=False
    if(pattern.shape[2] == 4 and auto_rotate_if_trans):
        # 有透明度通道且开启了旋转匹配
        have_alpha = True
        best_max_val = -1
        best_max_loc = (0, 0)
        for i in range(-3, 4):
            degree = i
            # 旋转
            rotate_pattern = rotate_image_with_transparency(pattern, degree)
            # 以透明部分作为mask
            rotate_mask = rotate_pattern[:, :, 3]  # 透明通道
            rotate_mask[rotate_mask>0] = 255
            rotate_pattern = rotate_pattern[:, :, :3] # 去除透明通道
            # https://www.cnblogs.com/FHC1994/p/9123393.html
            if not check_the_pic_validity(screenshot_cvmat, rotate_pattern):
                return default_response
            result = cv2.matchTemplate(screenshot_cvmat, rotate_pattern, cv2.TM_CCORR_NORMED, mask=rotate_mask)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            # print("角度为{}时，最大匹配值为{}".format(degree, max_val))
            if max_val>best_max_val:
                best_max_val = max_val
                best_max_loc = max_loc
        min_val, max_val, min_loc, max_loc = 0, best_max_val, 0, best_max_loc
    else:
        # 无旋转匹配
        # TODO： 多点匹配：https://pyimagesearch.com/2021/03/29/multi-template-matching-with-opencv/
        if pattern.shape[2] == 4:
            # 有透明度通道
            # 以透明部分作为mask
            pattern_mask = pattern[:, :, 3]  # 透明通道
            pattern_mask[pattern_mask>0] = 255
            pattern = pattern[:, :, :3] # 去除透明通道
            if not check_the_pic_validity(screenshot_cvmat, pattern):
                return default_response
            result = cv2.matchTemplate(screenshot_cvmat, pattern, cv2.TM_CCOEFF_NORMED, mask=pattern_mask)
        else:
            # 无透明度通道
            if not check_the_pic_validity(screenshot_cvmat, pattern):
                return default_response
            result = cv2.matchTemplate(screenshot_cvmat, pattern[:,:,:3], cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    h, w, _ = pattern.shape
    top_left = max_loc
    # get the center of the pattern
    center_x = top_left[0] + int(w / 2)
    center_y = top_left[1] + int(h / 2)
    if (show_result):
        bottom_right = (top_left[0] + w, top_left[1] + h)
        # draw a rectangle on the screenshot
        cv2.rectangle(screenshot_cvmat, top_left, bottom_right, (0, 255, 0), 2)
        # draw a circle on the center of the pattern
        cv2.circle(screenshot_cvmat, (center_x, center_y), 10, (0, 0, 255), -1)
        print("max_val: ", max_val)
        cv2.imshow('Matched Screenshot', screenshot_cvmat)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if(max_val >= threshold):
        # logging.debug("Pattern {} matched ({}). Center: ({}, {})".format(patternpic, max_val, center_x, center_y))
        return (True, (center_x, center_y), max_val)
    return (False, (0, 0), max_val)

def filter_num(input: str):
    """filter the number in the string"""
    return "".join(filter(str.isdigit, input))

def ocr_pic_area(image_mat, fromx, fromy, tox, toy, multi_lines = False, ocr_lang = OCR_LANG.EN):
    """
    get the string in the image area
    
    axis in image is x: from left to right, y: from top to bottom
    
    """
    ocr_sys = OCR_SYS_EN
    if ocr_lang == OCR_LANG.ZHS:
        ocr_sys = OCR_SYS_ZHS
    elif ocr_lang == OCR_LANG.ZHT:
        ocr_sys = OCR_SYS_ZHT
    fromx = int(fromx)
    fromy = int(fromy)
    tox = int(tox)
    toy = int(toy)
    def replace_mis(ocr_text):
        """
        替换容易识别错误的字符
        """
        ocr_text = ocr_text.strip()
        ocr_text = ocr_text.replace("９", "9")
        return ocr_text
    
    def local2global_pos(pixel_pos):
        """
        将局部坐标转换为全局坐标
        """
        return [int(pixel_pos[0]+fromx), int(pixel_pos[1]+fromy)]

    rawImage = image_mat
    if rawImage is None:
        if not multi_lines:
            return ["",0]
        else:
            return [["",0]]
    else:
        rawImage = rawImage[fromy:toy, fromx:tox]
        if not multi_lines:
            # 图像识别单行
            resstring = ocr_sys.ocr_single_line(rawImage)
            return [replace_mis(resstring[0]), resstring[1] if not isnan(resstring[1]) else 0]
        else:
            # 图像识别多行
            resstring_list = ocr_sys.detect_and_ocr(rawImage)
            return [[replace_mis(res.ocr_text), res.score if not isnan(res.score) else 0, [local2global_pos(res.box[0]), local2global_pos(res.box[2])]] for res in resstring_list]
    
def match_pixel_color_range(image_mat, x, y, low_range, high_range, printit = False):
    """
    match whether the color at that location is between the range
    
    x, y: the location of the pixel in the cv image
    low_range: (120, 120, 120) bgr of a color
    high_range: (125, 125, 125) bgr of a color
    
    return True if the color is between the range
    """
    img = image_mat
    if img is None:
        logging.error("Image Matrix is None when trying to match pixel color")
        return
    x = int(x)
    y = int(y)
    pixel = img[y, x][:3]
    if printit:
        print("Pixel color at ({}, {}): {}".format(x, y, pixel))
    # logging.info(f"Pixel color at ({x}, {y}): {pixel}")
    if (pixel[0] >= low_range[0] and pixel[0] <= high_range[0] and pixel[1] >= low_range[1] and pixel[1] <= high_range[1] and pixel[2] >= low_range[2] and pixel[2] <= high_range[2]):
        return True
    return False
    
def compare_diff(img1, img2, xfocus, yfocus):
    """
    比较img1和img2的不同，返回这些不同的元素的中心点坐标列表
    
    Parameters
    ----------
    img1 : np.ndarray
        图片1
    img2 : np.ndarray
        图片2
    xfocus : List[int]
        关注的x范围, 图片坐标
    yfocus : List[int]
        关注的y范围, 图片坐标
    """
    # 忽略UI部分
    # xs = [1, 1279]
    # ys = [124, 568]
    xs=[int(each) for each in xfocus]
    ys=[int(each) for each in yfocus]
    
    img1 = img1[ys[0]:ys[1], xs[0]:xs[1]]
    img2 = img2[ys[0]:ys[1], xs[0]:xs[1]]
    # img3为差异图
    img3 = cv2.bitwise_xor(img1, img2)
    img3[img3 != 0] = 255
    # 缩横着的影子
    kernel = np.ones((20, 5), np.uint8)
    img4 = cv2.erode(img3, kernel)
    # 再缩5x5
    kernel = np.ones((5, 5), np.uint8)
    img4 = cv2.erode(img4, kernel)
    
    
    # 转换为gray灰度图
    gray = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY)
    # 寻找轮廓
    contours, hier = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_positions = []
    # 这里得到的contours是一个list，每个元素都是一个ndarray，是轮廓的坐标
    for cidx,cnt in enumerate(contours):
        # 其中，x是轮廓的左上角x坐标，y是轮廓的左上角y坐标，w是轮廓的宽度，h是轮廓的高度
        (x, y, w, h) = cv2.boundingRect(cnt)
        # print('RECT: x={}, y={}, w={}, h={}'.format(x, y, w, h))
        # 如果面积比100小，就忽略
        if cv2.contourArea(cnt) < 300:
            continue
        # 原图绘制圆形
        # cv2.rectangle(originimg2, pt1=(x+xs[0], y+ys[0]), pt2=(x+w+xs[0], y+h+ys[0]),color=(255, 0, 0), thickness=3)
        # 添加中心点到final_positions
        final_positions.append((x+xs[0]+w//2, y+ys[0]+h//2))
    return final_positions


drawing = False  # 检查是否正在绘制
start_x, start_y = -1, -1
quick_return_data = None
quick_return_full_data = None
quick_return_full_data_blueprint = {
    'x':-1,
    'y':-1,
    'b':-1,
    'g':-1,
    'r':-1,
    'imgname':"",
    'imgx1':-1,
    'imgy1':-1,
    'imgx2':-1,
    'imgy2':-1
}
def screencut_tool(left_click = True, right_click = True, img_path = None, quick_return = False, quick_return_full = False, save_cut_img = True, save_folder_path = None):
    """
    截图工具
    
    Parameters
    ----------
    left_click : bool
        是否开启左键点击事件
    right_click : bool
        是否开启右键点击事件
    img_path : string
        要截取的图片路径
    quick_return : bool
        是否开启快速返回, 如果开启，点击右键后会返回坐标
    quick_return_full: bool
        快速返回后返回完整的json信息
    save_cut_img: bool
        是否保存截取的图片，默认保存
    save_folder_path: str
        截取后的图片的保存文件夹 如果为None则保存到当前目录
    """
    window_name = 'Screenshot'
    global start_x, start_y, drawing, quick_return_data, quick_return_full_data, quick_return_full_data_blueprint
    drawing = False  # 检查是否正在绘制
    start_x, start_y = -1, -1
    quick_return_data = ""
    quick_return_full_data = quick_return_full_data_blueprint.copy()
    # 读取透明度层
    if not img_path:
        screenshot = cv2.imread("./{}".format(config.userconfigdict['SCREENSHOT_NAME']))
    else:
        screenshot = cv2.imread(img_path)
    # 判断None
    if screenshot is None:
        logging.info("The screen shot picture is None")
        return "" if not quick_return_full else {}
    # 平均最大最小bgr
    bgr_result = [[],[],[]]
    def mouse_callback_s(event, x, y, flags, param):
        # 截图
        global start_x, start_y, drawing, quick_return_data, quick_return_full_data
        if right_click and event == cv2.EVENT_RBUTTONDOWN:  # 检查是否是鼠标右键键点击事件
            print(f"click: [{x}, {y}]", f"BGR: {[p for p in screenshot[y, x]]}")
            bgr_result[0].append(screenshot[y, x][0])
            bgr_result[1].append(screenshot[y, x][1])
            bgr_result[2].append(screenshot[y, x][2])
            print("min max avg bgr: ", np.min(bgr_result, axis=1), np.max(bgr_result, axis=1), np.mean(bgr_result, axis=1))
            
            if quick_return:
                quick_return_data = [x, y]
                # ---
                quick_return_full_data['x'] = x
                quick_return_full_data['y'] = y
                quick_return_full_data['b'] = bgr_result[0]
                quick_return_full_data['g'] = bgr_result[1]
                quick_return_full_data['r'] = bgr_result[2]
                cv2.destroyAllWindows()
            
        if left_click and event == cv2.EVENT_LBUTTONDOWN:  # 检查是否是鼠标左键按下事件
            drawing = True
            start_x, start_y = x, y
        elif left_click and event == cv2.EVENT_MOUSEMOVE:  # 检查是否是鼠标移动事件
            if drawing:
                screenshot_copy = screenshot.copy()  # 创建截图的副本
                cv2.rectangle(screenshot_copy, (start_x, start_y), (x, y), (0, 255, 0), 2)
                cv2.imshow(window_name, screenshot_copy)
        elif event == cv2.EVENT_LBUTTONUP:  # 检查是否是鼠标左键释放事件
            drawing = False
            end_x, end_y = x, y
            # cv2.rectangle(screenshot, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            cv2.imshow(window_name, screenshot)

            # 保存截取的区域到当前目录
            selected_region = screenshot[min(start_y,end_y):max(start_y,end_y), min(start_x,end_x):max(start_x,end_x)]
            nowstr = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
            filename = "selected_"+nowstr+".png"
            file_save_folder = "./" if save_folder_path is None else save_folder_path
            file_save_path = os.path.join(file_save_folder, filename)
            if save_cut_img:
                cv2.imwrite(file_save_path, selected_region)
                print(f"选定区域已被保存为/Saved as {file_save_path}")
            print(f"坐标点为起点[{start_x}, {start_y}] 终点[{end_x}, {end_y}]")
            print(f"cut code = [{start_y}:{end_y}, {start_x}:{end_x}]")

            if quick_return:
                quick_return_data = file_save_path
                # -----
                quick_return_full_data['imgname'] = file_save_path
                quick_return_full_data['imgx1'] = start_x
                quick_return_full_data['imgy1'] = start_y
                quick_return_full_data['imgx2'] = end_x
                quick_return_full_data['imgy2'] = end_y
                cv2.destroyAllWindows()
    
    # window can change size
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    # window initial size
    cv2.resizeWindow(window_name, screenshot.shape[1], screenshot.shape[0])
    cv2.imshow(window_name, screenshot)
    cv2.setMouseCallback(window_name, mouse_callback_s)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if quick_return:
        if quick_return_full:
            return quick_return_full_data
        else:
            return quick_return_data
    



def find_color_diff_positions(start_from_xy, distance, pic_data, vertical = True, range_pixels = 10, threshold = 20):
    """
    记录颜色发生变化的边缘坐标

    返回坐标列表

    start_from_xy: 
        起始坐标
    distance: 
        变化范围
    pic_data: 
        图片数据
    vertical: 
        是否垂直变化
    range_pixels: 
        采样像素间隔
    threshold: 
        颜色变化的阈值
    """
    color_change_coords = []
    last_color = pic_data[start_from_xy[1]][start_from_xy[0]]
    range_index = 1 if vertical else 0
    for range_p in range(start_from_xy[range_index], start_from_xy[range_index] + distance + 1, range_pixels):
        # 获取当前坐标的颜色
        # 图片坐标系
        x_pos = start_from_xy[0] if vertical else range_p
        y_pos = range_p if vertical else start_from_xy[1]
        color = pic_data[y_pos][x_pos]
        # 算颜色的各个分量的差值之和
        color_diff = abs(int(color[0]) - int(last_color[0])) + abs(int(color[1]) - int(last_color[1])) + abs(int(color[2]) - int(last_color[2]))
        # 如果颜色变化大于，记录坐标
        if color_diff > threshold:
            color_change_coords.append((x_pos, y_pos))
        last_color = color
    return color_change_coords

def find_pairs_distance_greater_than(point_list, distance):
    """
    找到距离大于distance的两点坐标

    返回两两坐标组合的列表

    point_list: 
        坐标列表
    distance: 
        距离阈值
    """
    result = []
    if len(point_list) < 2:
        return result
    for i in range(len(point_list)-1):
        if abs(point_list[i][0] - point_list[i+1][0]) + abs(point_list[i][1] - point_list[i+1][1]) > distance:
            result.append((point_list[i], point_list[i+1]))
    return result