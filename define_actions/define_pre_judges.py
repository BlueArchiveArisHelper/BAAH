from .basic_objects import *
from modules.utils import *

_pre_judges = [
    # 数字大于
    SubPreJudgeObj(
        id_name='num_greater', 
        compare_gui_name='num_greater',
        compare_method=lambda a, b: a > b,
        compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
    ),
    # 数字小于
    SubPreJudgeObj(
        id_name='num_less', 
        compare_gui_name='num_less',
        compare_method=lambda a, b: a < b,
        compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
    ),
    # 字符串/数字 等于
    SubPreJudgeObj(
        id_name='equal', 
        compare_gui_name='equal',
        compare_method=lambda a, b: str(a) == str(b),
        compare_value=ParamsObj('value', ParamsTypes.STRING, '')
    ),
    # 字符串/数字 不等于
    SubPreJudgeObj(
        id_name='not_equal', 
        compare_gui_name='not_equal',
        compare_method=lambda a, b: str(a) != str(b),
        compare_value=ParamsObj('value', ParamsTypes.STRING, '')
    ),
    # 字符串包含
    SubPreJudgeObj(
        compare_gui_name="include",
        id_name='include',
        compare_method=lambda a, b: str(b) in str(a),
        compare_value=ParamsObj('value', ParamsTypes.STRING, '')
    ),
    # 字符串不包含
    SubPreJudgeObj(
        compare_gui_name="not_include",
        id_name='not_include',
        compare_method=lambda a, b: str(b) not in str(a),
        compare_value=ParamsObj('value', ParamsTypes.STRING, '')
    ),
    # 永远为真
    SubPreJudgeObj(
        id_name='always_true', 
        compare_gui_name='always_true',
        compare_method=lambda a, b: True,
        compare_value=ParamsObj('value', ParamsTypes.STRING, '')
    ),
]