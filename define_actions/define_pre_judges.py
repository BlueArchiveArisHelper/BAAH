from .basic_objects import *
from modules.utils import *

# 被比较值类型是由实例种类固定的（compare_value), 比较对象是可更改的（compare_obj)

_pre_judges = [
    # 数字大于
    SubPreJudgeObj(
        id_name='num_greater_p', 
        compare_gui_name='num_greater_p',
        compare_method=lambda a, b: int(a) > b if type(a) == str else a > b,
        compare_values=[ParamsObj('value', ParamsTypes.NUMBER, 0)],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 数字小于
    SubPreJudgeObj(
        id_name='num_less_p', 
        compare_gui_name='num_less_p',
        compare_method=lambda a, b: int(a) < b if type(a) == str else a < b,
        compare_values=[ParamsObj('value', ParamsTypes.NUMBER, 0)],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 字符串/数字 等于
    SubPreJudgeObj(
        id_name='equal_p', 
        compare_gui_name='equal_p',
        compare_method=lambda a, b: str(a) == str(b),
        compare_values=[ParamsObj('value', ParamsTypes.STRING, '')],
        compare_obj = action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 字符串/数字 不等于
    SubPreJudgeObj(
        id_name='not_equal_p', 
        compare_gui_name='not_equal_p',
        compare_method=lambda a, b: str(a) != str(b),
        compare_values=[ParamsObj('value', ParamsTypes.STRING, '')],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 字符串包含
    SubPreJudgeObj(
        compare_gui_name="include_p",
        id_name='include_p',
        compare_method=lambda a, b: str(b) in str(a),
        compare_values=[ParamsObj('value', ParamsTypes.STRING, '')],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 字符串不包含
    SubPreJudgeObj(
        compare_gui_name="not_include_p",
        id_name='not_include_p',
        compare_method=lambda a, b: str(b) not in str(a),
        compare_values=[ParamsObj('value', ParamsTypes.STRING, '')],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
    # 像素点颜色近似
    SubPreJudgeObj(
        compare_gui_name="pixel_similar_p",
        id_name='pixel_similar_p',
        compare_method=lambda bgr, b, g, r: abs(bgr[0] - b)<=5 and abs(bgr[1] - g)<=5 and abs(bgr[2] - r)<=5,
        compare_values=[
            ParamsObj('B', ParamsTypes.NUMBER, 0),
            ParamsObj('G', ParamsTypes.NUMBER, 0),
            ParamsObj('R', ParamsTypes.NUMBER, 0)
        ],
        compare_obj=action_id2obj['get_pixel_color_a'].return_copy()
    ),
    # 永远为真
    SubPreJudgeObj(
        id_name='always_true_p', 
        compare_gui_name='always_true_p',
        compare_method=lambda a, b: True,
        compare_values=[ParamsObj('value', ParamsTypes.STRING, '')],
        compare_obj=action_id2obj['ocr_pic_a'].return_copy()
    ),
]