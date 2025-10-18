from .basic_objects import *
from modules.utils import *

def ifelse_action(precondition, action_main, action_precond_failed):
    """
    执行该操作对象
    """
    if precondition:
        if precondition.call_judge():
            if action_main:
                return action_main.call_func()
        else:
            if action_precond_failed:
                return action_precond_failed.call_func()
    else:
        if action_main:
            return action_main.call_func()
    return None

_flow_items = [
    FlowItemObj(
        id_name="ifelse_action",
        flowitem_gui_name="ifelse_action",
        id=None,
        inner_logic_func=ifelse_action,
        inner_func_objs=[
            prejudge_id2obj["always_true"].return_copy(), 
            action_id2obj["click_xy"].return_copy(), 
            action_id2obj["click_xy"].return_copy()
        ]
    )
]