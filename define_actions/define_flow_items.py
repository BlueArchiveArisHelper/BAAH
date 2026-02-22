from .basic_objects import *
from modules.utils import *
# from modules.AllTask import Task

def ifelse_action(precondition, action_main, action_precond_failed):
    """
    执行该操作对象
    """
    logging.info("Doing if-else action...")
    screenshot()
    if precondition:
        if precondition.call_func():
            if action_main:
                return action_main.call_func()
        else:
            if action_precond_failed:
                return action_precond_failed.call_func()
    else:
        if action_main:
            return action_main.call_func()
    return False

def run_until_action(maxtimes_param, action_obj, condition):
    """
    执行该操作对象直到满足条件或者达到最大执行次数
    """
    logging.info("Doing run_until action...")
    return logic_run_until(
        action_obj.call_func,
        condition.call_func,
        int(maxtimes_param.call_func()) # 执行ParamObj获取最大执行次数
    )

def do_single_action(action_obj):
    screenshot()
    action_obj.call_func()

_flow_items = [
    FlowItemObj(
        id_name="ifelse_action_f",
        flowitem_gui_name="ifelse_action_f",
        id=None,
        inner_logic_func=ifelse_action,
        inner_func_objs=[
            prejudge_id2obj["equal_p"].return_copy(), 
            action_id2obj["click_xy_a"].return_copy(), 
            action_id2obj["click_xy_a"].return_copy()
        ],
        format_render_str="ifelse_action_f_pattern"
    ),
    FlowItemObj(
        id_name="run_until_f",
        flowitem_gui_name="run_until_f",
        id=None,
        inner_logic_func=run_until_action,
        inner_func_objs=[
            ParamsObj("maxtimes", "maxtimes", ParamsTypes.NUMBER, 5), 
            action_id2obj["click_xy_a"].return_copy(), 
            prejudge_id2obj["equal_p"].return_copy(), 
        ],
        format_render_str="run_until_f_pattern"
    ),
    FlowItemObj(
        id_name="do_action_f",
        flowitem_gui_name="do_action_f",
        id=None,
        inner_logic_func=do_single_action,
        inner_func_objs=[
            action_id2obj["click_xy_a"].return_copy()
        ],
        format_render_str="do_action_f_pattern"
    )
]