# 字符串列表 与 模拟器操作的 映射转换
import time
import enum
import random
import secrets
import string
from modules.utils import *

def generate_secure_random_string(length=5):
    characters = string.ascii_letters + string.digits
    # 使用 secrets.choice 确保随机性适用于安全场景
    secure_random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return secure_random_string

# =============参数对象================

class ParamsTypes(enum.Enum):
    NUMBER = 1
    STRING = 2
    PICPATH = 3

class ParamsObj:
    """
    操作涉及到的参数对象

    包含参数名称，参数类型，参数值

    Parameters:
        param_gui_name: str, 参数名称
        param_type: ParamsTypes, 参数类型，GUI根据这个渲染不同的输入框
        param_value: any, 参数值
    """
    def __init__(self, param_gui_name:str=None, param_type:ParamsTypes=None, param_value=None):
        self.param_gui_name = param_gui_name  # 参数名称
        self.param_type = ParamsTypes(param_type)  # 参数类型
        self.param_value = param_value # 参数值
    
    def return_copy(self):
        return ParamsObj(self.param_gui_name, self.param_type, self.param_value)

    def load_from_dict(self, param_items:dict):
        if not param_items:
            return self
        # gui_name不应当依赖于读取json文件存储，只应当依赖于已有对象
        # self.param_gui_name = param_items.get('param_gui_name', None)  # 参数名称
        # self.param_type = param_items.get('param_type', None)  # 参数类型
        self.param_value = param_items.get('p_v', None) # 参数值
        return self
    
    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            # 'param_gui_name': self.param_gui_name,
            # 'param_type': self.param_type.value if self.param_type else None,
            'p_v': self.param_value
        }

# ============操作内容对象，需要注意预定义种类和复用问题================
# 用户勾选选择添加新的操作内容：默认显示action_id2obj里所有的GUI key作为头，当用户选择某个GUI key后，找到对应的SubActionMainObj实例，调用return_copy()返回一个新的对象，在GUI里进行修改
# GUI从json文件中读取配置文件里保存的操作内容：使用load_action_main_from_dictlist函数读取，根据GUI key在action_id2obj找到对应实例，return_copy()返回一个ActionMainObj对象，并把读取的参数值覆盖

class SubActionMainObj:
    """
    操作内容对象的基类

    包含：
        操作名称(标识符)
        操作名称（GUI显示）
        操作函数
        操作参数列表（默认为对应参数数量的空值）
    
    执行后可能需要返回出来一个变量
    """
    def __init__(self, action_id_name:str, action_gui_name:str, action_func, action_params:list[ParamsObj]):
        self.action_id_name = action_id_name  # 操作标识符
        self.action_gui_name = action_gui_name  # 操作名称
        self.action_func = action_func # 操作函数
        self.action_params = action_params # 操作参数列表
    
    def return_copy(self):
        """
        由于需要复用多个预先定义的操作，这里以返回一个新的对象的方式来避免引用问题
        """
        return SubActionMainObj(
            self.action_id_name,
            self.action_gui_name,
            self.action_func,
            [ParamsObj(param.param_gui_name, param.param_type, param.param_value) for param in self.action_params]
        )

    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            'a_id_n': self.action_id_name,
            # 'action_gui_name': self.action_gui_name,
            'a_p': [param.to_json_dict() for param in self.action_params]
        }
    
    def call_func(self):
        """
        调用操作函数，并传入参数
        """
        if not self.action_func:
            return None
        param_values = [param.param_value for param in self.action_params]
        return self.action_func(*param_values)

# 只有action_id_name, action_params需要从json文件中读取修改，其他参数使用预定义的实例里的
# SubActionMainObj实例：
# 点击图片
subAction_click_pic = SubActionMainObj(
    action_id_name='click_pic',
    action_gui_name='click_pic',
    action_func=lambda pic: click(pic),
    action_params=[
        ParamsObj('picPath', ParamsTypes.PICPATH, '')
    ]
)
# 点击坐标
subAction_click_xy = SubActionMainObj(
    action_id_name='click_xy',
    action_gui_name='click_xy',
    action_func=lambda x, y: click((int(x), int(y))),
    action_params=[
        ParamsObj('x', ParamsTypes.NUMBER, 0),
        ParamsObj('y', ParamsTypes.NUMBER, 0)
    ]
)
# ocr
subAction_ocr_pic = SubActionMainObj(
    action_id_name='ocr_pic',
    action_gui_name='ocr_pic',
    action_func=lambda x1, y1, x2, y2: ocr_area((x1, y1), (x2, y2))[0],
    action_params=[
        ParamsObj('left_up_x', ParamsTypes.NUMBER, 0),
        ParamsObj('left_up_y', ParamsTypes.NUMBER, 0),
        ParamsObj('right_down_x', ParamsTypes.NUMBER, 100),
        ParamsObj('right_down_y', ParamsTypes.NUMBER, 100),
    ]

)


# 若干个action实例 与 action_id_name的映射关系
# 使用这些实例的时候需要调用return_copy()来返回一个新的对象
action_id2obj = {
    subAction_click_pic.action_id_name: subAction_click_pic,
    subAction_click_xy.action_id_name: subAction_click_xy,
    # ...
    subAction_ocr_pic.action_id_name: subAction_ocr_pic,
}

def load_action_main_from_dict(action_items):
    """
    读取json文件中保存的操作内容，转换成ActionMainObj对象
    """
    if not action_items:
        return None
    _action_id_name = action_items.get('a_id_n', None)
    if not _action_id_name or _action_id_name not in action_id2obj:
        return None
    _sub_action = action_id2obj[_action_id_name].return_copy()
    # 读取参数
    _params = action_items.get('a_p', [])
    for i in range(min(len(_params), len(_sub_action.action_params))):
        # 只把参数值覆盖到模板参数对象里，其他参数保持预定义的
        _sub_action.action_params[i].load_from_dict(_params[i])
    return _sub_action


# ============前置条件对象================

# class CompareMethods(enum.Enum):
#     EQUAL = 1 # 数字相等
#     NOT_EQUAL = 2
#     GREATER = 3
#     LESS = 4
#     CONTAINS = 5 # 字符串包含
#     NOT_CONTAINS = 6
#     EXIST = 7 # 图片存在
#     NOT_EXIST = 8 


class SubPreJudgeObj:
    """
    操作前置判断对象

    包含：
        被比较对象（通过ActionMainObj执行后返回的值）
        比较方式
        比较值（ParamsObj）
    """
    def __init__(self, compare_id_name:str, compare_gui_name:str, compare_method:callable,  compare_value:ParamsObj, compare_obj:SubActionMainObj=None):
        self.compare_id_name = compare_id_name  # 比较标识符
        self.compare_gui_name = compare_gui_name # 比较名称
        self.compare_method = compare_method # 比较方式，函数
        self.compare_value = compare_value # 指定被比较值（类型）
        self.compare_obj = compare_obj # 被比较对象，通过ActionMainObj执行后返回的值
        

    def call_judge(self):
        if not self.compare_obj or not self.compare_method:
            return False
        obj_value = self.compare_obj.call_func()
        return self.compare_method(obj_value, self.compare_value.param_value)
    
    def to_json_dict(self):
        return {
            'c_id_n': self.compare_id_name,
            # 'compare_gui_name': self.compare_gui_name,
            'c_obj': self.compare_obj.to_json_dict() if self.compare_obj else None,
            'c_v': self.compare_value.to_json_dict() if self.compare_value else None,
        }

    def return_copy(self):
        return SubPreJudgeObj(
            compare_id_name = self.compare_id_name,
            compare_gui_name = self.compare_gui_name,
            compare_method = self.compare_method,
            compare_obj = self.compare_obj, # 这里不用深拷贝，每个PreJudge里的compare_obj都是独立赋值的
            compare_value = self.compare_value.return_copy()
        )

# 前置操作具体子类
subPreJudge_Num_Equal = SubPreJudgeObj(
    compare_id_name='num_equal',
    compare_gui_name='num_equal',
    compare_method=lambda a, b: a == b,
    compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
)
subPreJudge_Num_NotEqual = SubPreJudgeObj(
    compare_id_name='num_not_equal',
    compare_gui_name='num_not_equal',
    compare_method=lambda a, b: a != b,
    compare_value=ParamsObj('value', ParamsTypes.NUMBER, 0)
)


# 若干个prejudge实例 与 compare_id_name的映射关系
prejudge_id2obj = {
    subPreJudge_Num_Equal.compare_id_name: subPreJudge_Num_Equal,
    subPreJudge_Num_NotEqual.compare_id_name: subPreJudge_Num_NotEqual,
    # ...
}

def load_prejudge_from_dict(action_items):
    """
    读取json文件中保存的前置条件，转换成SubPreJudgeObj对象
    """
    if not action_items:
        return None
    _compare_id_name = action_items.get('c_id_n', None)
    if not _compare_id_name or _compare_id_name not in prejudge_id2obj:
        return None
    # 使用return_copy()来避免引用问题
    _sub_prejudge = prejudge_id2obj[_compare_id_name].return_copy()
    # 前置条件的被比较对象
    _compare_obj_dict = action_items.get('c_obj', None)
    if _compare_obj_dict:
        _sub_prejudge.compare_obj = load_action_main_from_dict(_compare_obj_dict)
    # 前置条件的比较值ParamsObj, 只覆盖值
    _sub_prejudge.compare_value.load_from_dict(action_items.get('c_v', None))
    return _sub_prejudge


# ============操作对象================

class FlowActionObj:
    """
    操作对象，多个对象链式可以组合成一个操作序列

    每个对象包含:
        该操作的id（时间戳）
        操作前置条件（可选）
        操作内容（操作名称 + 操作参数，执行时调用对应的操作函数）
        不符合前置条件时的操作内容（当有前置条件时）
    """
    def __init__(self, 
                precondition:SubPreJudgeObj=None, 
                action_main:SubActionMainObj=None, 
                action_precond_failed:SubActionMainObj=None, 
                id:str=None, # 标识id,无指定标识id的时候生成时间戳id
                ):
        self.precondition = precondition  # 前置条件
        self.action_main = action_main # 主要操作
        self.action_precond_failed = action_precond_failed  # 前置条件不满足时的处理方式
        self.action_id = id if id else generate_secure_random_string()  # 操作id
    
    @staticmethod
    def load_from_dict(action_items):
        """
        读取json文件中保存的操作对象，转换成FlowActionObj对象
        """
        targetobj = FlowActionObj()
        if not action_items:
            return targetobj
        targetobj.action_id = action_items.get('a_id', None)
        targetobj.precondition = load_prejudge_from_dict(action_items.get('p_c', None))
        targetobj.action_main = load_action_main_from_dict(action_items.get('a_m', None))
        targetobj.action_precond_failed = load_action_main_from_dict(action_items.get('a_p_f', None))
        return targetobj

    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            'a_id': self.action_id,
            'p_c': self.precondition.to_json_dict() if self.precondition else None,
            'a_m': self.action_main.to_json_dict() if self.action_main else None,
            'a_p_f': self.action_precond_failed.to_json_dict() if self.action_precond_failed else None,
        }
    
    def call_action(self):
        """
        执行该操作对象
        """
        if self.precondition:
            if self.precondition.call_judge():
                if self.action_main:
                    return self.action_main.call_func()
            else:
                if self.action_precond_failed:
                    return self.action_precond_failed.call_func()
        else:
            if self.action_main:
                return self.action_main.call_func()
        return None

        
# ============操作组对象================

class EmulatorActionGroup:
    """
    用户操作的链式组合，维护用户操作的相关状态和内容

    包含：
        操作对象列表
        操作关联的状态字典
    """
    def __init__(self):
        pass

    def load_from_dictlist(self, action_group_items:list[FlowActionObj]):
        pass

    def load_from_params(self, actions:list[FlowActionObj]=None, state_dict:dict=None):
        self.actions = actions if actions else []  # 操作对象列表
        self.state_dict = state_dict if state_dict else {}  # 操作关联的状态字典




if __name__ == "__main__":
    # 测试代码，挪到test.py里执行
    action_ocr = subAction_ocr_pic.return_copy()
    action_ocr.action_params[0].param_value = 250
    action_ocr.action_params[1].param_value = 397
    action_ocr.action_params[2].param_value = 320
    action_ocr.action_params[3].param_value = 436
    print(action_ocr.call_func())

    prejudge_eq = subPreJudge_Num_Equal.return_copy()
    prejudge_eq.compare_value.param_value = "1457"
    prejudge_eq.compare_obj = action_ocr
    print(prejudge_eq.call_judge())

    action_click_xy_1 = subAction_click_xy.return_copy()
    action_click_xy_1.action_params[0].param_value = 1141
    action_click_xy_1.action_params[1].param_value = 69

    action_click_xy_2 = subAction_click_xy.return_copy()
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