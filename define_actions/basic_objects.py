import random
import secrets
import string
import enum
import zipfile
from nicegui import ui
from gui.components.cut_screenshot import screencut_button, cut_screenshot
from gui.components.get_app_entrance import get_app_entrance_button
from modules.utils import *

# ParamsObj, [SubActionMainObj, SubPreJudgeObj, FlowItemObj], FlowActionGroup
# 中括号包裹的是有预定义模板的，这些模板使得用户在GUI里能选择预定义的比较/操作
# 无包裹的类都是动态创建的实例类

# 共性：id_name属性, 有to_json_dict函数，load_from_dict函数，return_copy函数, call_func函数, render_gui函数
#=======================
# to_json_dict 必须导出 id_name，以及其他用户会改变的，需要持久化的参数
# return_copy 时，防止同名实例内参数被引用修改，用户能够修改的那些参数需要深拷贝
#=======================

# 定义跳转异常，靠异常捕获实现行号跳转
class FlowInterruptException(Exception):
    def __init__(self, message, target_id):
        super().__init__(message)
        self.target_id = target_id
    
    def __str__(self):
        return f"FlowInterruptException: {self.args[0]}"

def raise_flowinterrupt(target_id):
    raise FlowInterruptException(f"Jump to flow item id: {target_id}", target_id)

# 映射集合
action_id2obj = {}
prejudge_id2obj = {}
flowitem_id2obj = {}

def generate_secure_random_string(length=5):
    characters = string.ascii_letters + string.digits
    # 使用 secrets.choice 确保随机性适用于安全场景
    secure_random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return secure_random_string

def load_objs_from_list(param_obj_list, param_dict_list, match_by_id_name = True):
    """
    从param_dict_list里解析param_obj_list中的元素.
    
    - match_by_id_name 为 True时：

        1. 如果list中每项dict都有id_name，则按照id_name匹配。基于obj模板匹配dict，如果没有对应的dict（找不到id_name）则obj模板保持不变

        2. 如果list中dict缺少id_name，则按照顺序匹配

    - match_by_id_name 为 False时：

        按照顺序匹配

    """
    all_has_id_name = True
    for paramd in param_dict_list:
        if 'id_n' not in paramd:
            all_has_id_name = False
            break
    # 匹配，基于item_list
    if all_has_id_name and match_by_id_name:
        # 构造 name:param_dict_list元素映射表
        param_dict_map = {each['id_n']:each for each in param_dict_list}
        for obj in param_obj_list:
            # 如果能找到这个item对应的dict
            if obj.id_name in param_dict_map:
                obj.load_from_dict(param_dict_map.get(obj.id_name))
            else:
                logging.error(istr({
                    CN: f"未能找到 {obj.id_name} 对应的json元素，模板加载为初始值。现有json keys为 {param_dict_map.keys()}",
                    EN: f"Can not find json item for {obj.id_name}, instance load as initial value. Keys set is {param_dict_map.keys()}"
                }))
    else:
        # 按顺序匹配
        for i in range(min(len(param_obj_list), len(param_dict_list))):
            # 只把参数值覆盖到模板参数对象里，其他参数保持预定义的
            param_obj_list[i].load_from_dict(param_dict_list[i])
    return param_obj_list

# =============参数对象================

# 与ParamsObj的render_gui相关
class ParamsTypes(enum.Enum):
    NUMBER = 1
    STRING = 2
    PICPATH = 3
    APKPACKAGE = 4

class ParamsObj:
    """
    操作涉及到的参数对象

    包含参数名称，参数类型，参数值

    Parameters:
        id_name: id属性,需要json与模板保持一致，用以读取json
        param_gui_name: str, 参数名称
        param_type: ParamsTypes, 参数类型，GUI根据这个渲染不同的输入框
        param_value: any, 参数值
    """
    def __init__(self, id_name:str, gui_name=None, param_type:ParamsTypes=None, param_value=None):
        self.id_name = id_name # 参数名称，与参数的读取与解析有关，不要轻易改变
        self.param_gui_name = gui_name if gui_name else id_name  # 参数gui名称
        self.param_type = ParamsTypes(param_type)  # 参数类型
        self.param_value = param_value # 参数值
    
    def return_copy(self):
        return ParamsObj(self.id_name, self.param_gui_name, self.param_type, self.param_value)

    def load_from_dict(self, param_items:dict):
        """从dict里读取param value值，不会验证id_name"""
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
            'id_n': self.id_name,
            # 'param_gui_name': self.param_gui_name,
            # 'param_type': self.param_type.value if self.param_type else None,
            'p_v': self.param_value
        }
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def call_func(self):
        return self.param_value
    
    def render_gui(self, dataconfig):
        if self.param_type == ParamsTypes.NUMBER:
            ui.number(label=self.param_gui_name).bind_value(self, 'param_value').style("width:100px")
        elif self.param_type == ParamsTypes.STRING:
            ui.input(label=self.param_gui_name).bind_value(self, 'param_value').style("width:100px")
        elif self.param_type == ParamsTypes.PICPATH:
            with ui.column():
                screencut_button(inconfig=dataconfig, resultdict=self, resultkey='param_value')
        elif self.param_type == ParamsTypes.APKPACKAGE:
            with ui.column():
                get_app_entrance_button(inconfig=dataconfig, resultdict=self, resultkey="param_value")
        else:
            ui.label(f"Unkown param type: {self.param_type}")
    

# ============操作内容对象，需要注意预定义种类和复用问题================
# 用户勾选选择添加新的操作内容：默认显示action_id2obj里所有的GUI key作为头，当用户选择某个GUI key后，找到对应的SubActionMainObj实例，调用return_copy()返回一个新的对象，在GUI里进行修改
# GUI从json文件中读取配置文件里保存的操作内容：使用load_action_main_from_dictlist函数读取，根据GUI key在action_id2obj找到对应实例，return_copy()返回一个ActionMainObj对象，并把读取的参数值覆盖

class LineQuickEditType(enum.Enum):
    POINT_XY = 1
    BGR_VALUES = 2
    REGION_XYXY = 3
    # REGION_PICPATH = 4 # PICPATH 在 ParamObj gui层面就能通过按钮快速编辑了

def quick_edit_button(quick_edit_type, inconfig, params_list:list[ParamsObj], edit_value_map):
    left_click = False
    right_click = False
    # ======
    if (quick_edit_type in [LineQuickEditType.POINT_XY, LineQuickEditType.BGR_VALUES]):
        right_click = True
    if (quick_edit_type in [LineQuickEditType.REGION_XYXY]):
        left_click = True
    # =====
    def call_back_func(_full_pick_result,  _params_list:list[ParamsObj], _edit_value_map):
        # 对于 edit_value_map 里的每个key:name，找到其key对应的full_pick_result值，填到对应name的ParamObj里
        for key in _edit_value_map:
            if key not in _full_pick_result:
                print(f"No key {key} in full_pick_result")
                continue
            # 找到对应的值
            val = _full_pick_result[key]
            name = _edit_value_map[key]
            # 找到name的ParamObj
            _f = False
            for param in _params_list:
                if param.id_name == name:
                    param.param_value = val
                    _f = True
                    break
            if not _f:
                print(f"Can not find ParamsObj named: {name}")
    # 按钮
    ui.button(
        "EDIT",
        on_click=lambda _params_list=params_list, _edit_value_map = edit_value_map: cut_screenshot(
            inconfig=inconfig,
            resultdict=None,
            resultkey=None,
            left_click=left_click,
            right_click=right_click,
            quick_return=True,
            callback=lambda fullres, __params_list=_params_list, __edit_value_map=_edit_value_map: call_back_func(fullres, __params_list, __edit_value_map),
            quick_return_full = True,
            save_cut_img = False
        )
    )
    

class SubActionMainObj:
    """
    操作内容对象的基类

    包含：
        操作名称(标识符)
        操作名称（GUI显示）
        操作函数
        操作参数列表（默认为对应参数数量的空值）
        按钮快速截图编辑种类类型

    
    执行后可能需要返回出来一个变量
    """
    def __init__(self, id_name:str, action_gui_name:str, action_func, action_params:list[ParamsObj], line_edit_type: LineQuickEditType, edit_value_map):
        self.id_name = id_name  # 操作标识符
        self.action_gui_name = action_gui_name  # 操作名称
        self.action_func = action_func # 操作函数
        self.action_params = action_params # 操作参数列表
        self.line_edit_type = line_edit_type # 按钮快速截图编辑种类类型
        self.edit_value_map = edit_value_map # 快速截图编辑结果映射
    
    def return_copy(self):
        """
        由于需要复用多个预先定义的操作，这里以返回一个新的对象的方式来避免引用问题
        """
        return SubActionMainObj(
            self.id_name,
            self.action_gui_name,
            self.action_func,
            [param.return_copy() for param in self.action_params], # json读取覆盖ParamsObj值
            self.line_edit_type,
            self.edit_value_map # 不会修改这变量
        )

    def to_json_dict(self):
        """
        转换成json可保存的字典格式
        """
        return {
            'id_n': self.id_name,
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
            if self.line_edit_type:
                quick_edit_button(
                    quick_edit_type=self.line_edit_type,
                    inconfig = dataconfig,
                    params_list = self.action_params,
                    edit_value_map = self.edit_value_map
                )
    
    def load_from_dict(self, action_items:dict):
        """
        根据dict里的key，找到对应的模板对象，读取json内数据，覆盖这整个self实例
        """
        new_instance = SubActionMainObj._load_action_main_from_dict(action_items)
        if new_instance is None:
            return
        self.__dict__.clear()
        self.__dict__.update(new_instance.__dict__)

    
    @staticmethod
    def _load_action_main_from_dict(action_items:dict):
        """
        读取json文件中保存的操作内容，转换成ActionMainObj对象
        """
        # 只有id_name, action_params需要从json文件中读取修改，其他参数使用预定义的实例里的
        if not action_items:
            return None
        _id_name = action_items.get('id_n', None)
        if not _id_name or _id_name not in action_id2obj:
            logging.error(istr({
                CN: f"无法在action_id2obj中找到 {_id_name}",
                EN: f"Can not find {_id_name} in action_id2obj"
            }))
            return None
        _sub_action:SubActionMainObj = action_id2obj[_id_name].return_copy()
        # 读取参数
        _params = action_items.get('a_p', [])
        load_objs_from_list(_sub_action.action_params, _params)
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
    def __init__(self, id_name:str, compare_gui_name:str, compare_method:callable,  compare_values:list[ParamsObj], compare_obj:SubActionMainObj):
        self.id_name = id_name  # 比较标识符
        self.compare_gui_name = compare_gui_name # 比较名称
        self.compare_method = compare_method # 比较方式，函数
        self.compare_values = compare_values # 指定被比较值（类型）
        self.compare_obj = compare_obj # 被比较对象，通过ActionMainObj执行后返回的值
        

    def call_func(self):
        if not self.compare_method:
            return False
        obj_value = self.compare_obj.call_func() if self.compare_obj else None
        return self.compare_method(obj_value, *[cv.param_value for cv in self.compare_values])
    
    def to_json_dict(self):
        return {
            'id_n': self.id_name,
            # 'compare_gui_name': self.compare_gui_name,
            'c_obj': self.compare_obj.to_json_dict() if self.compare_obj else None,
            'c_v': [cv.to_json_dict() for cv in self.compare_values] if self.compare_values else [],
        }

    def return_copy(self):
        return SubPreJudgeObj(
            id_name = self.id_name,
            compare_gui_name = self.compare_gui_name,
            compare_method = self.compare_method,
            compare_obj = self.compare_obj.return_copy() if self.compare_obj else None, # load时会读json new覆盖
            compare_values = [cv.return_copy() for cv in self.compare_values] # load时json读取改变
        )

    def render_gui(self, dataconfig):
        @ui.refreshable
        def sub_pre_judge_area():
            with ui.column():
                if self.compare_obj:
                    with ui.row():
                        ui.label("比较对象:")
                        # 提供修改下层组件的能力
                        ui.select({k:dataconfig.get_text(k) for k in action_id2obj}, value=self.compare_obj.id_name, on_change=lambda v: change_compare_obj(v.value))
                        self.compare_obj.render_gui(dataconfig)
                # with ui.row():
                #     # 上级组件提供对下级组件的修改能力，所以这边不能修改这个SubPreJudge的种类，只能更改这SubPreJudge的内部参数
                #     ui.label(self.compare_gui_name)
                if self.compare_values:
                    with ui.row():
                        ui.label("比较值:")
                        # 只会更新ParamsObj里的属性值
                        for cv in self.compare_values:
                            cv.render_gui(dataconfig)
        sub_pre_judge_area()
        
        def change_compare_obj(new_id_name):
            # 替换被比较对象,更新实例
            new_obj = action_id2obj[new_id_name].return_copy()
            self.compare_obj = new_obj
            # 刷新GUI
            sub_pre_judge_area.refresh()
    
    def load_from_dict(self, prejudge_items:dict):
        """
        根据dict里的key，找到对应的模板对象，读取json内数据，覆盖这个self实例
        """
        new_instance = SubPreJudgeObj._load_prejudge_from_dict(prejudge_items)
        if new_instance is None:
            return
        self.__dict__.clear()
        self.__dict__.update(new_instance.__dict__)


    @staticmethod
    def _load_prejudge_from_dict(prejudge_items:dict):
        """
        读取json文件中保存的前置条件，转换成SubPreJudgeObj对象
        """
        if not prejudge_items:
            return None
        _id_name = prejudge_items.get('id_n', None)
        if not _id_name or _id_name not in prejudge_id2obj:
            logging.error(istr({
                CN: f"无法在prejudge_id2obj中找到 {_id_name}",
                EN: f"Can not find {_id_name} in prejudge_id2obj"
            }))
            return None
        # 使用return_copy()来避免引用问题
        _sub_prejudge:SubPreJudgeObj = prejudge_id2obj[_id_name].return_copy()
        # 前置条件的被比较对象
        _compare_obj_dict = prejudge_items.get('c_obj', None)
        if _compare_obj_dict:
            _sub_prejudge.compare_obj.load_from_dict(_compare_obj_dict)
        # 前置条件的比较值ParamsObj, 只覆盖值
        load_objs_from_list(_sub_prejudge.compare_values, prejudge_items.get('c_v', []))
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
            'id_n': self.id_name,
            'id': self.id,
            # 内部逻辑函数不保存
            'i_f_o': [obj.to_json_dict() for obj in self.inner_func_objs] if self.inner_func_objs else []
        }
            
    def call_func(self):
        self.inner_logic_func(*self.inner_func_objs)

    def render_gui(self, dataconfig):
        format_str_list = dataconfig.get_text(self.format_render_str).split('#')
        @ui.refreshable
        def flow_item_area():
            # ui.label(f'操作对象: {self.flowitem_gui_name} (ID: {self.id})')
            item_ptr = 0 # 指向列表对象
            while(item_ptr < len(format_str_list)):
                # 迭代item直到遇到非label
                while(item_ptr < len(format_str_list)):
                    item = format_str_list[item_ptr]
                    if not item.startswith("%"):
                        ui.label(item)
                        item_ptr += 1
                    else:
                        # 遇到非label元素
                        break
                # 解析这个非label
                # %开头则替换为对应下标的内部子组件
                # 把#%0#替换为内部逻辑函数对象
                if item_ptr >= len(format_str_list):
                    # 越界
                    break
                item = format_str_list[item_ptr]
                index = int(item[1:])
                if index >= 0 and index < len(self.inner_func_objs):
                    obj = self.inner_func_objs[index]
                    with ui.row():
                        if isinstance(obj, SubActionMainObj):
                            # ActionMainObj组件
                            ui.select({k:dataconfig.get_text(k) for k in action_id2obj}, value=obj.id_name, on_change=lambda v,idx=index: change_inner_action_func_obj(v.value, idx))
                            obj.render_gui(dataconfig)
                        elif isinstance(obj, SubPreJudgeObj):
                            # SubPreJudgeObj组件
                            ui.select({k:dataconfig.get_text(k) for k in prejudge_id2obj}, value=obj.id_name, on_change=lambda v,idx=index: change_inner_prejudge_func_obj(v.value, idx))
                            obj.render_gui(dataconfig)
                        elif isinstance(obj, ParamsObj):
                            # ParamsObj组件
                            obj.render_gui(dataconfig)
                else:
                    ui.label(f"字符串索引超出范围: {item}")
                item_ptr += 1
        
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
    
    def load_from_dict(self, flow_items:dict):
        """
        根据dict里的key，找到对应的模板对象，读取json内数据，覆盖这个self实例
        """
        new_instance = FlowItemObj._load_flow_item_from_dict(flow_items)
        if new_instance is None:
            return
        self.__dict__.clear()
        self.__dict__.update(new_instance.__dict__)


    @staticmethod
    def _load_flow_item_from_dict(flow_items:dict):
        """
        读取json文件中保存的操作对象，转换成FlowItemObj对象
        """
        if not flow_items:
            return None
        _id_name = flow_items.get('id_n', None)
        if not _id_name or _id_name not in flowitem_id2obj:
            logging.error(istr({
                CN: f"无法在flowitem_id2obj中找到 {_id_name}",
                EN: f"Can not find {_id_name} in flowitem_id2obj"
            }))
            return None
        # 使用return_copy()来避免引用问题
        _flow_item:FlowItemObj = flowitem_id2obj[_id_name].return_copy()
        # 读取id
        _flow_item.id = flow_items.get('id', None)
        # 读取内部逻辑函数对象列表
        _inner_func_objs_dictlist = flow_items.get('i_f_o', [])
        if _inner_func_objs_dictlist:
            # FlowItem内具体执行什么操作是在json内保存的（用户可以改变某个inner_func_objs的种类）。不能根据模板内id_name去匹配json内id_n，会由于找不到对应json key直接跳过并重置成模板初始参数。直接按顺序加载所有json格式的inner_func_objs进实例即可， match_by_id_name = False
            load_objs_from_list(_flow_item.inner_func_objs, _inner_func_objs_dictlist, match_by_id_name = False)
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

    def load_from_dict(self, action_group_item:dict):
        try:
            for item in action_group_item.get('a_l', []):
                action_obj = FlowItemObj._load_flow_item_from_dict(item)
                if action_obj:
                    self.action_list.append(action_obj)
            return self
        except:
            logging.error(traceback.format_exc())
            return self
    
    def to_json_dict(self):
        return {
            'a_l': [action.to_json_dict() for action in self.action_list],
            # 's_d': self.status_dict # 状态字典不保存,每次运行重新生成
        }
    
    def save_flow_into_zip(self):
        """
        将该操作内容打包成zip文件，zip文件内包含一个json文件保存操作内容的结构化信息，以及操作内容里涉及到的图片文件（如果有的话）
        """
        al_json = self.to_json_dict()
        # 使用re找到所有 *.png 格式的字符串，保存到all_pic_paths里
        all_pic_paths = set()
        def find_pic_paths(obj, pic_set):
            for k in obj:
                # 得到集合对象内部元素
                if isinstance(obj, list):
                    v = k
                elif isinstance(obj, dict):
                    v = obj[k]
                else:
                    print(f"Unkown type in find_pic_paths: {type(obj)}")
                # 字符串元素处理匹配png
                if isinstance(v, str) and v.endswith('.png'):
                    pic_set.add(v)
                # 递归处理集合类型元素
                elif isinstance(v, list) or isinstance(v, dict):
                    find_pic_paths(v, pic_set)
        find_pic_paths(al_json, all_pic_paths)
        print(f"package pics: {all_pic_paths}")
        # 压缩成zip文件，命名为flow_{timestamp}.zip
        zip_filename = f"flow_{int(time.time())}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # 写入json文件
            zipf.writestr('flow.json', json.dumps(al_json, indent=4))
            # 写入图片文件
            for pic_path in all_pic_paths:
                if os.path.exists(pic_path):
                    zipf.write(pic_path)
                else:
                    print(f"Pic path not exists: {pic_path}")
        # 弹出nicegui提醒
        ui.notify(f"Flow saved into {zip_filename}", color="green")


    def render_gui(self, dataconfig):
        @ui.refreshable
        def flow_group_area():
            with ui.column():
                # 第一行，添加按钮 和 导出按钮
                with ui.row():
                    ui.button(dataconfig.get_text("button_add"), on_click=lambda x:add_flow_item(0))
                    ui.button("Save", on_click=self.save_flow_into_zip)
                for i,action in enumerate(self.action_list):
                    with ui.card():
                        # 每个 action block
                        with ui.row():
                            with ui.column():
                                with ui.row().style("align-items: center;"):
                                    ui.select({k:dataconfig.get_text(k) for k in flowitem_id2obj}, value=action.id_name, on_change=lambda v,idx=i: change_flow_item_obj(v.value, idx))
                                    ui.label(f"ID: {action.id}")
                                action.render_gui(dataconfig)
                        with ui.row():
                            # 该行下方添加
                            ui.button(dataconfig.get_text("button_add"), on_click=lambda x,idx=i:add_flow_item(idx+1))
                            # 删除该行
                            ui.button(dataconfig.get_text("button_delete"), on_click=lambda x,idx=i: del_flow_item(idx), color="red")
        flow_group_area()

        def change_flow_item_obj(new_id_name, obj_index):
            # 替换操作对象,更新实例
            new_obj = flowitem_id2obj[new_id_name].return_copy()
            # 保留id
            new_obj.id = self.action_list[obj_index].id
            self.action_list[obj_index] = new_obj
            # 刷新GUI
            flow_group_area.refresh()
        
        def add_flow_item(line_index):
            """
            添加一个操作对象在line_index处，原先index处被往后挤
            """
            # 插入一个默认的操作对象
            default_flow_item = list(flowitem_id2obj.values())[-1].return_copy()
            self.action_list.insert(line_index, default_flow_item)
            flow_group_area.refresh()
        
        def del_flow_item(line_index):
            """
            删除一个操作对象
            """
            self.action_list.pop(line_index)
            flow_group_area.refresh()

    def _find_corresponding_flow_item_index_by_id(self, target_id):
        """
        通过id查找对应的flow item index
        """
        for ind,action in enumerate(self.action_list):
            if action.id == target_id:
                return ind
        return -1
    
    def run_flow(self):
        """
        执行整个操作链，返回是否无报错执行
        """
        try:
            ind = 0
            while(ind < len(self.action_list)):
                try:
                    action = self.action_list[ind]
                    logging.info(f"flow {ind+1}/{len(self.action_list)}, id: {action.id}")
                    action.call_func()
                except FlowInterruptException as fie:
                    target_index = self._find_corresponding_flow_item_index_by_id(fie.target_id)
                    logging.info(f"Flow interrupted, jump to id: {fie.target_id}, index: {target_index}")
                    if target_index == -1:
                        logging.error(f"Can not find flow item with id: {fie.target_id}, stop execution")
                        return False
                    else:
                        ind = target_index - 1 # -1是因为for循环会+1
                ind += 1
            return True
        except: # 内部如果发生FlowInterruptException以外的异常
            logging.error(traceback.format_exc())
        return False
