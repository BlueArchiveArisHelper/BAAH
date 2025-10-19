from .basic_objects import *
from modules.utils import *

def screen_shot_ocr(x1, y1, x2, y2):
    screenshot()
    return ocr_area((int(x1), int(y1)), (int(x2), int(y2)))[0]

_main_actions = [
    SubActionMainObj(
        id_name='click_pic',
        action_gui_name='click_pic',
        action_func=lambda pic: click(pic),
        action_params=[
            ParamsObj('picPath', ParamsTypes.PICPATH, '')
        ]
    ),
    SubActionMainObj(
        id_name='click_xy',
        action_gui_name='click_xy',
        action_func=lambda x, y: click((int(x), int(y))),
        action_params=[
            ParamsObj('x', ParamsTypes.NUMBER, 0),
            ParamsObj('y', ParamsTypes.NUMBER, 0)
        ]
    ),
    SubActionMainObj(
        id_name='ocr_pic',
        action_gui_name='ocr_pic',
        action_func=screen_shot_ocr,
        action_params=[
            ParamsObj('left_up_x', ParamsTypes.NUMBER, 0),
            ParamsObj('left_up_y', ParamsTypes.NUMBER, 0),
            ParamsObj('right_down_x', ParamsTypes.NUMBER, 100),
            ParamsObj('right_down_y', ParamsTypes.NUMBER, 100),
        ]
    )
]