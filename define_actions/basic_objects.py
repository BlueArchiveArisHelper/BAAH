import random
import secrets
import string
import enum
from nicegui import ui
from gui.components.cut_screenshot import screencut_button

# ParamsObj, [SubActionMainObj, SubPreJudgeObj, FlowItemObj], FlowActionGroup
# 中括号包裹的是有预定义模板的，这些模板使得用户在GUI里能选择预定义的比较/操作
# 无包裹的类都是动态创建的实例类

# 共性：id_name属性, 有to_json_dict函数，return_copy函数, call_func函数, render_gui函数
#=======================
# to_json_dict 必须导出 id_name，以及其他用户会改变的，需要持久化的参数
# return_copy 时，防止同名实例内参数被引用修改，用户能够修改的那些参数需要深拷贝
#=======================

# 映射集合
action_id2obj = {}
prejudge_id2obj = {}
flowitem_id2obj = {}

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
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def render_gui(self, dataconfig):
        if self.param_type == ParamsTypes.NUMBER:
            ui.number(label=self.param_gui_name).bind_value(self, 'param_value')
        elif self.param_type == ParamsTypes.STRING:
            ui.input(label=self.param_gui_name).bind_value(self, 'param_value')
        elif self.param_type == ParamsTypes.PICPATH:
            with ui.column():
                screencut_button(inconfig=dataconfig, resultdict=self, resultkey='param_value')
        else:
            ui.label(f"Unkown param type: {self.param_type}")
    

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
    def __init__(self, id_name:str, action_gui_name:str, action_func, action_params:list[ParamsObj]):
        self.id_name = id_name  # 操作标识符
        self.action_gui_name = action_gui_name  # 操作名称
        self.action_func = action_func # 操作函数
        self.action_params = action_params # 操作参数列表
    
    def return_copy(self):
        """
        由于需要复用多个预先定义的操作，这里以返回一个新的对象的方式来避免引用问题
        """
        return SubActionMainObj(
            self.id_name,
            self.action_gui_name,
            self.action_func,
            [param.return_copy() for param in self.action_params] # json读取覆盖ParamsObj值
        )

    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            'a_id_n': self.id_name,
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
    
    def render_gui(self, dataconfig):
        """
        在GUI里渲染该操作内容的参数输入框
        """
        # 上层组件提供对下层组件的修改能力，所以这边不能修改这个SubAction的种类，只能更改这SubAction的内部参数
        with ui.row():
            for i, param in enumerate(self.action_params):
                param.render_gui(dataconfig)


# 只有id_name, action_params需要从json文件中读取修改，其他参数使用预定义的实例里的
def load_action_main_from_dict(action_items:dict):
    """
    读取json文件中保存的操作内容，转换成ActionMainObj对象
    """
    if not action_items:
        return None
    _id_name = action_items.get('a_id_n', None)
    if not _id_name or _id_name not in action_id2obj:
        return None
    _sub_action:SubActionMainObj = action_id2obj[_id_name].return_copy()
    # 读取参数
    _params = action_items.get('a_p', [])
    for i in range(min(len(_params), len(_sub_action.action_params))):
        # 只把参数值覆盖到模板参数对象里，其他参数保持预定义的
        _sub_action.action_params[i].load_from_dict(_params[i])
    return _sub_action



# ============前置条件对象================
# 实例多态

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
    def __init__(self, id_name:str, compare_gui_name:str, compare_method:callable,  compare_value:ParamsObj, compare_obj:SubActionMainObj):
        self.id_name = id_name  # 比较标识符
        self.compare_gui_name = compare_gui_name # 比较名称
        self.compare_method = compare_method # 比较方式，函数
        self.compare_value = compare_value # 指定被比较值（类型）
        self.compare_obj = compare_obj # 被比较对象，通过ActionMainObj执行后返回的值
        

    def call_func(self):
        if not self.compare_obj or not self.compare_method:
            return False
        obj_value = self.compare_obj.call_func()
        return self.compare_method(obj_value, self.compare_value.param_value)
    
    def to_json_dict(self):
        return {
            'c_id_n': self.id_name,
            # 'compare_gui_name': self.compare_gui_name,
            'c_obj': self.compare_obj.to_json_dict() if self.compare_obj else None,
            'c_v': self.compare_value.to_json_dict() if self.compare_value else None,
        }

    def return_copy(self):
        return SubPreJudgeObj(
            id_name = self.id_name,
            compare_gui_name = self.compare_gui_name,
            compare_method = self.compare_method,
            compare_obj = self.compare_obj.return_copy(), # load时会读json new覆盖
            compare_value = self.compare_value.return_copy() # load时json读取改变
        )

    def render_gui(self, dataconfig):
        @ui.refreshable
        def sub_pre_judge_area():
            with ui.row():
                with ui.column():
                    ui.label("被比较对象:")
                    # 提供修改下层组件的能力
                    ui.select({k:k for k in action_id2obj}, value=self.compare_obj.id_name, on_change=lambda v: change_compare_obj(v.value))
                    self.compare_obj.render_gui(dataconfig)
                with ui.column():
                    # 上级组件提供对下级组件的修改能力，所以这边不能修改这个SubPreJudge的种类，只能更改这SubPreJudge的内部参数
                    ui.label(self.compare_gui_name)
                with ui.column():
                    ui.label("比较值:")
                    # 只会更新ParamsObj里的属性值
                    self.compare_value.render_gui(dataconfig)
        sub_pre_judge_area()
        
        def change_compare_obj(new_id_name):
            # 替换被比较对象,更新实例
            new_obj = action_id2obj[new_id_name].return_copy()
            self.compare_obj = new_obj
            # 刷新GUI
            sub_pre_judge_area.refresh()
    


def load_prejudge_from_dict(action_items:dict):
    """
    读取json文件中保存的前置条件，转换成SubPreJudgeObj对象
    """
    if not action_items:
        return None
    _id_name = action_items.get('c_id_n', None)
    if not _id_name or _id_name not in prejudge_id2obj:
        return None
    # 使用return_copy()来避免引用问题
    _sub_prejudge:SubPreJudgeObj = prejudge_id2obj[_id_name].return_copy()
    # 前置条件的被比较对象
    _compare_obj_dict = action_items.get('c_obj', None)
    if _compare_obj_dict:
        _sub_prejudge.compare_obj = load_action_main_from_dict(_compare_obj_dict)
    # 前置条件的比较值ParamsObj, 只覆盖值
    _sub_prejudge.compare_value.load_from_dict(action_items.get('c_v', None))
    return _sub_prejudge


# ============操作对象================
# 实例多态
class FlowItemObj:
    """
    操作对象，多个对象链式可以组合成一个操作序列

    每个对象包含:
        该操作的id名称
        该操作的gui名称
        该操作的时间戳唯一标识符
        内部逻辑函数
        内部逻辑函数所需的SubPreJudgeObj和SubActionMainObj对象
        
    """
    def __init__(self, 
                id_name,
                flowitem_gui_name,
                id:str, # 标识id,无指定标识id的时候生成时间戳id
                inner_logic_func:callable,
                inner_func_objs:list,
                format_render_str:str
                ):
        self.id_name = id_name
        self.flowitem_gui_name = flowitem_gui_name
        self.id = id if id else generate_secure_random_string()  # 操作id
        self.inner_logic_func = inner_logic_func
        self.inner_func_objs = inner_func_objs if inner_func_objs else []
        self.format_render_str = format_render_str # 用于GUI显示的格式化字符串
        
    def return_copy(self):
        return FlowItemObj(
            self.id_name,
            self.flowitem_gui_name,
            None, # id，load时会读json new覆盖，新建时生成新的id
            self.inner_logic_func,
            [func_obj.return_copy() for func_obj in self.inner_func_objs], # load时会读json new覆盖，新建时copy新的
            self.format_render_str
        )

    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            'f_id_n': self.id_name,
            'id': self.id,
            # 内部逻辑函数不保存
            'i_f_o': [obj.to_json_dict() for obj in self.inner_func_objs] if self.inner_func_objs else []
        }

    def load_func_objs_from_dictlist(self, objs_json_list):
        # 从json列表里读取内部对象
        for i,item in enumerate(objs_json_list):
            # 找到对应的模板里的inner_func_objs
            target_item = self.inner_func_objs[i]
            # 判断id_name
            if target_item.id_name in action_id2obj:
                # ActionMainObj
                self.inner_func_objs[i] = load_action_main_from_dict(item)
            elif target_item.id_name in prejudge_id2obj:
                # SubPreJudgeObj
                self.inner_func_objs[i] = load_prejudge_from_dict(item)
            
    def call_func(self):
        self.inner_logic_func(*self.inner_func_objs)

    def render_gui(self, dataconfig):
        format_str_list = self.format_render_str.split('#')
        @ui.refreshable
        def flow_item_area():
            ui.label(f'操作对象: {self.flowitem_gui_name} (ID: {self.id})')
            for i,stritem in enumerate(format_str_list):
                if stritem.startswith("%"):
                    # 替换为内部逻辑函数对象 #%0#
                    index = int(stritem[1:])
                    if index >= 0 and index < len(self.inner_func_objs):
                        obj = self.inner_func_objs[index]
                        if obj.id_name in action_id2obj:
                            # ActionMainObj
                            ui.select({k:k for k in action_id2obj}, value=obj.id_name, on_change=lambda v,idx=index: change_inner_action_func_obj(v.value, idx))
                            obj.render_gui(dataconfig)
                        elif obj.id_name in prejudge_id2obj:
                            # SubPreJudgeObj
                            ui.select({k:k for k in prejudge_id2obj}, value=obj.id_name, on_change=lambda v,idx=index: change_inner_prejudge_func_obj(v.value, idx))
                            obj.render_gui(dataconfig)
                    else:
                        ui.label(f"索引超出范围: {stritem}")
                else:
                    # 文字部分直接label显示
                    ui.label(stritem)
        
        flow_item_area()
        def change_inner_action_func_obj(new_id_name, obj_index):
            # 替换内部逻辑函数对象,更新实例
            new_obj = action_id2obj[new_id_name].return_copy()
            self.inner_func_objs[obj_index] = new_obj
            # 刷新GUI
            flow_item_area.refresh()

        def change_inner_prejudge_func_obj(new_id_name, obj_index):
            # 替换内部逻辑函数对象,更新实例
            new_obj = prejudge_id2obj[new_id_name].return_copy()
            self.inner_func_objs[obj_index] = new_obj
            # 刷新GUI
            flow_item_area.refresh()



def load_flow_item_from_dict(action_item:dict):
    """
    读取json文件中保存的操作对象，转换成FlowItemObj对象
    """
    if not action_item:
        return None
    _id_name = action_item.get('f_id_n', None)
    if not _id_name or _id_name not in flowitem_id2obj:
        return None
    # 使用return_copy()来避免引用问题
    _flow_item:FlowItemObj = flowitem_id2obj[_id_name].return_copy()
    # 读取id
    _flow_item.id = action_item.get('id', None)
    # 读取内部逻辑函数对象列表
    _inner_func_objs_dictlist = action_item.get('i_f_o', [])
    if _inner_func_objs_dictlist:
        _flow_item.load_func_objs_from_dictlist(_inner_func_objs_dictlist)
    return _flow_item

# ============操作组对象================

class FlowActionGroup:
    """
    用户操作的链式组合，维护用户操作的相关状态和内容

    包含：
        操作对象列表
        操作关联的状态字典
    """
    def __init__(self, action_list:list[FlowItemObj] = None, status_dict = None):
        self.action_list = action_list if action_list else [] # 操作对象列表
        self.status_dict = status_dict if status_dict else {} # 操作关联的状态字典

    def load_from_dictlist(self, action_group_item:dict):
        for item in action_group_item.get('a_l', []):
            action_obj = load_flow_item_from_dict(item)
            if action_obj:
                self.action_list.append(action_obj)
        return self
    
    def to_json_dict(self):
        return {
            'a_l': [action.to_json_dict() for action in self.action_list],
            # 's_d': self.status_dict
        }

    def render_gui(self, dataconfig):
        @ui.refreshable
        def flow_group_area():
            for i,action in enumerate(self.action_list):
                ui.select({k:k for k in flowitem_id2obj}, value=action.id_name, on_change=lambda v,idx=i: change_flow_item_obj(v.value, idx))
                action.render_gui(dataconfig)
                # 删除该行
                ui.button(dataconfig.get_text("button_delete"), on_click=lambda x,i=i: del_flow_item(i))
            # 最后一行，添加按钮
            ui.button(dataconfig.get_text("button_add"), on_click=lambda x:add_flow_item(len(self.action_list)-1))
        flow_group_area()

        def change_flow_item_obj(new_id_name, obj_index):
            # 替换操作对象,更新实例
            new_obj = flowitem_id2obj[new_id_name].return_copy()
            self.action_list[obj_index] = new_obj
            # 刷新GUI
            flow_group_area.refresh()
        
        def add_flow_item(line_index):
            """
            添加一个操作对象
            """
            # 插入一个默认的操作对象
            default_flow_item = list(flowitem_id2obj.values())[0].return_copy()
            self.action_list.insert(line_index+1, default_flow_item)
            flow_group_area.refresh()
        
        def del_flow_item(line_index):
            """
            删除一个操作对象
            """
            self.action_list.pop(line_index)
            flow_group_area.refresh()
    
    def run_flow(self):
        """
        执行整个操作链
        """
        for action in self.action_list:
            action.call_func()
