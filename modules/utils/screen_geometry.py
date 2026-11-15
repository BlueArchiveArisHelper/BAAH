from modules.configs.MyConfig import config

REFERENCE_WIDTH = 1280
REFERENCE_HEIGHT = 720

def is_horizontal_screen(width, height):
    """判断是否是横屏分辨率"""
    return width >= height

def is_720p(width, height, rotate_free = False):
    """判断是否是720p分辨率，rotate_free判定是否开启旋转无关匹配"""
    if rotate_free:
        # 匹配旋转无关的720p分辨率
        longer_side = max(width, height)
        shorter_side = min(width, height)
        return longer_side == REFERENCE_WIDTH and shorter_side == REFERENCE_HEIGHT
    return width == REFERENCE_WIDTH and height == REFERENCE_HEIGHT

def is_169ratio(width, height, rotate_free = False):
    """判断是否是横屏16:9比例，且最少为720p，rotate_free判定是否开启旋转无关匹配"""
    if rotate_free:
        # 匹配旋转无关的16:9比例
        longer_side = max(width, height)
        shorter_side = min(width, height)
        return longer_side >= REFERENCE_WIDTH and shorter_side >= REFERENCE_HEIGHT and longer_side * 9 == shorter_side * 16
    return width >= REFERENCE_WIDTH and height >= REFERENCE_HEIGHT and width * 9 == height * 16


def to_native_point(x, y, native_width=None, native_height=None, use_config=None):
    """
    从720p逻辑坐标转换为当前分辨率的物理坐标，仅对16：9分辨率有效，其他分辨率直接返回原坐标
    
    优先使用传入的具体宽高数据，如果native_width和native_height参数为None，则使用use_config的session数据进行转换。
    """
    if use_config is None:
        use_config = config
    # 有native_width和native_height参数时，优先使用参数值，否则使用use_config的session数据
    if native_width is None or native_height is None:
        native_width = use_config.sessiondict.get("NATIVE_SCREENSHOT_WIDTH")
        native_height = use_config.sessiondict.get("NATIVE_SCREENSHOT_HEIGHT")
    if not is_169ratio(native_width, native_height, rotate_free=True):
        return x, y
    if is_horizontal_screen(native_width, native_height):
        return int(x * native_width / REFERENCE_WIDTH), int(y * native_height / REFERENCE_HEIGHT)
    else:
        # 竖屏状态逻辑宽度取720（REFERENCE_HEIGHT）， 逻辑高度取1280（REFERENCE_WIDTH）
        return int(x * native_width / REFERENCE_HEIGHT), int(y * native_height / REFERENCE_WIDTH)
