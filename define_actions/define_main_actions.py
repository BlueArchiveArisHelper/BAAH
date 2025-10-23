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
            ParamsObj('picPath', ParamsTypes.PICPATH, ''),
            ParamsObj('threshold', ParamsTypes.NUMBER, 0.9)
        ]
    ),
    SubActionMainObj(
        id_name='click_xy_a',
        action_gui_name='click_xy_a',
        action_func=lambda x, y: (
            logging.info(f"click {int(x)} {int(y)}"),
            click((int(x), int(y)))
        )[-1],
        action_params=[
            ParamsObj('x', ParamsTypes.NUMBER, 0),
            ParamsObj('y', ParamsTypes.NUMBER, 0)
        ]
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
            ParamsObj('left_up_x', ParamsTypes.NUMBER, 0),
            ParamsObj('left_up_y', ParamsTypes.NUMBER, 0),
            ParamsObj('right_down_x', ParamsTypes.NUMBER, 100),
            ParamsObj('right_down_y', ParamsTypes.NUMBER, 100),
        ]
    ),
    SubActionMainObj(
        id_name="sleep_time_a",
        action_gui_name="sleep_time_a",
        action_func=lambda t: (
            logging.info(f"sleep {t}s"),
            sleep(float(t))
        )[-1],
        action_params=[
            ParamsObj('time_seconds', ParamsTypes.NUMBER, 1)
        ]
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
            ParamsObj('x', ParamsTypes.NUMBER, 0),
            ParamsObj('y', ParamsTypes.NUMBER, 0)
        ]
    ),
    SubActionMainObj(
        id_name = "open_apk_package_a",
        action_gui_name = "open_apk_package_a",
        action_func=lambda strapp: (
            logging.info(f"Opening {strapp}"),
            open_app(strapp),
        )[-1],
        action_params=[
            ParamsObj("package", ParamsTypes.APKPACKAGE, "")
        ]
    ),
]