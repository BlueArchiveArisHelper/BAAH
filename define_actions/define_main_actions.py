from .basic_objects import *
from modules.utils import *


_main_actions = [
    SubActionMainObj(
        id_name='click_pic_a',
        action_gui_name='click_pic_a',
        action_func=lambda pic, thre: (
            logging.info(f"click {pic}"),
            click(pic, threshold=thre)
        )[-1],
        action_params=[
            ParamsObj('picPath', 'picPath', ParamsTypes.PICPATH, ''),
            ParamsObj('threshold', 'threshold', ParamsTypes.NUMBER, 0.9)
        ],
        line_edit_type=None,
        edit_value_map=None
    ),
    SubActionMainObj(
        id_name='click_xy_a',
        action_gui_name='click_xy_a',
        action_func=lambda x, y: (
            logging.info(f"click {int(x)} {int(y)}"),
            click((int(x), int(y)))
        )[-1],
        action_params=[
            ParamsObj('x', 'x', ParamsTypes.NUMBER, 0),
            ParamsObj('y', 'y', ParamsTypes.NUMBER, 0)
        ],
        line_edit_type=LineQuickEditType.POINT_XY,
        edit_value_map={
            'x':'x',
            'y':'y'
        }
    ),
    SubActionMainObj(
        id_name='scroll_xyxy_a',
        action_gui_name='scroll_xyxy_a',
        action_func=lambda x1, y1, x2, y2: (
            logging.info(f"swipe from {x1}, {y1} to {x2}, {y2}"),
            swipe((x1, y1), (x2, y2))
        )[-1],
        action_params=[
            ParamsObj('from_x', 'from_x', ParamsTypes.NUMBER, 0),
            ParamsObj('from_y', 'from_y', ParamsTypes.NUMBER, 0),
            ParamsObj('to_x', 'to_x', ParamsTypes.NUMBER, 0),
            ParamsObj('to_y', 'to_y', ParamsTypes.NUMBER, 0),
        ],
        line_edit_type=LineQuickEditType.REGION_XYXY,
        edit_value_map={
            'imgx1':'from_x',
            'imgy1':'from_y',
            'imgx2':'to_x',
            'imgy2':'to_y'
        }
    ),
    SubActionMainObj(
        id_name='ocr_pic_a',
        action_gui_name='ocr_pic_a',
        action_func=lambda x1, y1, x2, y2: (
            ocr_text := ocr_area((int(x1), int(y1)), (int(x2), int(y2)))[0],
            logging.info(f"ocr area: {x1}, {y1}-{x2}, {y2} is {ocr_text}"),
            ocr_text
        )[-1],
        action_params=[
            ParamsObj('left_up_x', 'left_up_x', ParamsTypes.NUMBER, 0),
            ParamsObj('left_up_y', 'left_up_y', ParamsTypes.NUMBER, 0),
            ParamsObj('right_down_x', 'right_down_x', ParamsTypes.NUMBER, 100),
            ParamsObj('right_down_y', 'right_down_y', ParamsTypes.NUMBER, 100),
        ],
        line_edit_type=LineQuickEditType.REGION_XYXY,
        edit_value_map={
            'imgx1':'left_up_x',
            'imgy1':'left_up_y',
            'imgx2':'right_down_x',
            'imgy2':'right_down_y'
        }
    ),
    SubActionMainObj(
        id_name="sleep_time_a",
        action_gui_name="sleep_time_a",
        action_func=lambda t: (
            logging.info(f"sleep {t}s"),
            sleep(float(t))
        )[-1],
        action_params=[
            ParamsObj('time_seconds', 'time_seconds', ParamsTypes.NUMBER, 1)
        ],
        line_edit_type=None,
        edit_value_map=None
    ),
    SubActionMainObj(
        id_name="get_pixel_color_a",
        action_gui_name="get_pixel_color_a",
        action_func=lambda x, y: (
            pixel_BGR := get_pixel((int(x), int(y))),
            logging.info(f"get pixel color: {pixel_BGR}"),
            pixel_BGR
        )[-1],
        action_params=[
            ParamsObj('x', 'x', ParamsTypes.NUMBER, 0),
            ParamsObj('y', 'y', ParamsTypes.NUMBER, 0)
        ],
        line_edit_type=LineQuickEditType.POINT_XY,
        edit_value_map={
            'x':'x',
            'y':'y'
        }
    ),
    SubActionMainObj(
        id_name = "open_apk_package_a",
        action_gui_name = "open_apk_package_a",
        action_func=lambda strapp: (
            logging.info(f"Opening {strapp}"),
            open_app(strapp),
        )[-1],
        action_params=[
            ParamsObj("package", "package", ParamsTypes.APKPACKAGE, "")
        ],
        line_edit_type=None,
        edit_value_map=None
    ),
    SubActionMainObj(
        id_name="jump_flow_item_id",
        action_gui_name="jump_flow_item_id",
        action_func=lambda flow_id: raise_flowinterrupt(flow_id.strip()),
        action_params=[
            ParamsObj('id', 'id', ParamsTypes.STRING, '')
        ],
        line_edit_type=None,
        edit_value_map=None
        
    )
]