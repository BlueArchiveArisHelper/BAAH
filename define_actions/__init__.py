# 字符串列表 与 模拟器操作的 映射转换
# modules.utils  -> <this> -> modules.AllTask
# gui.components ->        -> gui.pages
from .basic_objects import *

# 从 .define_actions/define_main_actions 和 .define_actions/define_pre_judges 加载预定义的操作和判断, 构成映射字典
from .define_main_actions import _main_actions
for obj in _main_actions:
    action_id2obj[obj.id_name] = obj
# pre judge 比较 action结果与给定参数，在action初始化之后导入
from .define_pre_judges import _pre_judges
for obj in _pre_judges:
    prejudge_id2obj[obj.id_name] = obj
# 等基本映射建立完毕后, 再加载流程控制类对象，否则_flow_items内部的inner_func_objs会取空
from .define_flow_items import _flow_items
for obj in _flow_items:
    flowitem_id2obj[obj.id_name] = obj



if __name__ == "__main__":
    # 测试代码，挪到test.py里执行
    # screencut_tool()
    
    action_ocr = action_id2obj["ocr_pic"].return_copy()
    action_ocr.action_params[0].param_value = 250
    action_ocr.action_params[1].param_value = 397
    action_ocr.action_params[2].param_value = 320
    action_ocr.action_params[3].param_value = 436
    print(action_ocr.call_func())

    prejudge_eq = prejudge_id2obj["equal"].return_copy()
    prejudge_eq.compare_value.param_value = "1738"
    prejudge_eq.compare_obj = action_ocr
    print(prejudge_eq.call_func())

    action_click_xy_1 = action_id2obj["click_xy"].return_copy()
    action_click_xy_1.action_params[0].param_value = 1141
    action_click_xy_1.action_params[1].param_value = 69

    action_click_xy_2 = action_id2obj["click_xy"].return_copy()
    action_click_xy_2.action_params[0].param_value = 1233
    action_click_xy_2.action_params[1].param_value = 74

    ifelse_action = flowitem_id2obj["ifelse_action"]
    ifelse_action.inner_func_objs=[
        prejudge_eq,
        action_click_xy_1,
        action_click_xy_2
    ]
    # ifelse_action.call_action()
    group = FlowActionGroup([ifelse_action])
    str_group = group.to_json_dict()
    print(str_group)
    ###

    parse_back_group = FlowActionGroup().load_from_dict(str_group)

    parse_back_group.run_flow()