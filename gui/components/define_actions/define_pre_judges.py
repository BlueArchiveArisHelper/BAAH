from .basic_objects import *
from modules.utils import *

_pre_judges = [
    SubPreJudgeObj(
        compare_id_name='num_equal',
        compare_gui_name='num_equal',
        compare_method=lambda a, b: a == b,
        compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
    ),
    SubPreJudgeObj(
        compare_id_name='num_not_equal',
        compare_gui_name='num_not_equal',
        compare_method=lambda a, b: a != b,
        compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
    )
]