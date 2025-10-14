# 字符串列表 与 模拟器操作的 映射转换
from modules.utils import *
from .basic_objects import *
from .define_main_actions import _main_actions
from .define_pre_judges import _pre_judges

# 从 .define_actions/define_main_actions 和 .define_actions/define_pre_judges 加载预定义的操作和判断, 构成映射字典
for obj in _main_actions:
    action_id2obj[obj.action_id_name] = obj
for obj in _pre_judges:
    prejudge_id2obj[obj.compare_id_name] = obj



if __name__ == "__main__":
    # 测试代码，挪到test.py里执行
    action_ocr = action_id2obj["ocr_pic"].return_copy()
    action_ocr.action_params[0].param_value = 250
    action_ocr.action_params[1].param_value = 397
    action_ocr.action_params[2].param_value = 320
    action_ocr.action_params[3].param_value = 436
    print(action_ocr.call_func())

    prejudge_eq = prejudge_id2obj["num_equal"].return_copy()
    prejudge_eq.compare_value.param_value = "1457"
    prejudge_eq.compare_obj = action_ocr
    print(prejudge_eq.call_judge())

    action_click_xy_1 = action_id2obj["click_xy"].return_copy()
    action_click_xy_1.action_params[0].param_value = 1141
    action_click_xy_1.action_params[1].param_value = 69

    action_click_xy_2 = action_id2obj["click_xy"].return_copy()
    action_click_xy_2.action_params[0].param_value = 1233
    action_click_xy_2.action_params[1].param_value = 74

    emulator_action = FlowActionObj(
        precondition=prejudge_eq,
        action_main = action_click_xy_1,
        action_precond_failed = action_click_xy_2
    )
    # emulator_action.call_action()

    str_action = emulator_action.to_json_dict()
    print(str_action)
    parse_back_action = FlowActionObj.load_from_dict(str_action)
    parse_back_action.call_action()