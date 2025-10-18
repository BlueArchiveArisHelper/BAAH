from .basic_objects import *
from modules.utils import *

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
        action_func=lambda x1, y1, x2, y2: ocr_area((x1, y1), (x2, y2))[0],
        action_params=[
            ParamsObj('left_up_x', ParamsTypes.NUMBER, 0),
            ParamsObj('left_up_y', ParamsTypes.NUMBER, 0),
            ParamsObj('right_down_x', ParamsTypes.NUMBER, 100),
            ParamsObj('right_down_y', ParamsTypes.NUMBER, 100),
        ]
    )
]