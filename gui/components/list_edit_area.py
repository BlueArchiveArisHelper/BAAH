from nicegui import ui
from .modern_ui import form_row, surface, operation_bar, notice_box
from modules.configs.MyConfig import config

def list_edit_area(datadict, linedesc, blockdesc="", has_switch=False, 
                   min_value_for_1st_dim = 1,min_value_for_2nd_dim = 1, min_value_for_3rd_dim = -99, *, blockdesc_as_notice=False, empty_line_prompt_id="config_no_data_set_here"):
    """
    datadict: 要修改的二维或三维列表，长度代表列表维度
        [str1, str2] 或 [str1, str2, [str3, str4]] 或 [str1, str2, [str3, str4, str5]]
    linedesc: 二维或三维列表的描述，长度代表列表维度
    blockdesc_as_notice: 是否将区块说明展示为提醒框，默认保持原有普通文字。
    blockdesc: 对于这个块的描述
    has_switch: 是否有单个元素的功能开关，有功能开关的话，二维列表会升三维，三维列表的最后一维会多一个值 表示开关
    min_value_for_1st_dim: 元素长度为3时元素中的第一维度（地区序号）的最小值，默认为1
    min_value_for_2nd_dim: 元素长度为3时元素中的第二维度（关卡序号）的最小值，默认为1
    min_value_for_3rd_dim: 元素长度为3时元素中的第三维度（关卡扫荡次数）的最小值，默认为-99
    """
    dim = len(linedesc)
    # 对列表的最后一维的元素的文字描述的数量
    # [关卡，次数] -> subdim = 2 = len(linedesc[2])
    # [地区，关卡，次数] -> subdim = 3 = len(linedesc[2])
    subdim = 0
    if dim >= 3:
        subdim = len(linedesc[2])
    # 列表共用卡片与操作栏，增删及数值约束保持原有逻辑。
    @ui.refreshable
    def item_list():
        # 说明的展示形式由调用方显式指定，不比较翻译后的内容。
        if blockdesc_as_notice and blockdesc:
            notice_box(blockdesc)
        else:
            for blocklinedesc in blockdesc.split('\n'):
                ui.label(f'{blocklinedesc}')
        for i in range(len(datadict)):
            line_item = datadict[i]
            ui.label(f'{config.get_text("config_nth")} {i+1} {linedesc[0]}: ')
            with form_row().classes("baah-list-items"):
                if len(line_item) == 0:
                    notice_box(config.get_text(empty_line_prompt_id), tone="warning")
                for j in range(len(line_item)):
                    if len(linedesc) == 2:
                        # 第i个地区的第j个教室, or 商店里的第i行第j个物品
                        if isinstance(datadict[i][j], tuple) or isinstance(datadict[i][j], list):
                            # 如果该元素是个元组或者列表，那么该元素应当包含一个开关
                            # [值，开关boolean]
                            with surface("baah-list-entry"):
                                ui.number(f'{linedesc[1]}',
                                    min=1,
                                    step=1,
                                    precision=0,
                                    format="%.0f",
                                    value=line_item[j][0],
                                    on_change=lambda v,i=i,j=j: datadict[i][j].__setitem__(0, int(v.value)),
                                    ).style('width: 128px')
                                if len(line_item[j]) == 2 and has_switch:
                                    ui.label(config.get_text("button_enable"))
                                    ui.switch(value=line_item[j][1],on_change=lambda v,i=i,j=j:datadict[i][j].__setitem__(1, bool(v.value)))
                        else:
                            # 否则就按照单个数字渲染
                            ui.number(f'{linedesc[1]}',
                                    min=1,
                                    step=1,
                                    precision=0,
                                    format="%.0f",
                                    value=line_item[j],
                                    on_change=lambda v,i=i,j=j: datadict[i].__setitem__(j, int(v.value)),
                                    ).style('width: 128px')
                    elif len(linedesc) == 3:
                        # 无副标题的列表不额外渲染孤立冒号，字段和值仍按原顺序显示。
                        if linedesc[1]:
                            ui.label(f'{linedesc[1]}:')
                        with form_row().classes("baah-list-items"):
                            with surface("baah-list-entry"):
                                for k in range(len(line_item[j])):
                                    # 如果一个元素的数据量超出了给定的文字描述的数量，而且是有开关的
                                    # 那么最后那个'多出来的'数据就是开关
                                    if k >= subdim: # 多出来的数据下标continue掉，没有对应的渲染文字
                                        if k == subdim and has_switch: # 如果刚好多一个数据而且has_switch就渲染个开关
                                            ui.label(config.get_text("button_enable"))
                                            ui.switch(value=line_item[j][k],on_change=lambda v,i=i,j=j:datadict[i][j].__setitem__(k, bool(v.value)))
                                        continue
                                    #  遍历地区, 关卡和次数
                                    min_value = min_value_for_1st_dim
                                    # 如果数据的位置就是最后一个文字描述的位置，代表的数据是扫荡次数，最小值为-99
                                    if k == subdim-1:
                                        min_value = min_value_for_3rd_dim
                                    # 如果数据的位置是倒数第二个文字描述的位置，代表数据对应扫荡的关卡序号
                                    if k == subdim-2:
                                        min_value = min_value_for_2nd_dim
                                    ui.number(f'{linedesc[2][k]}',
                                                min=min_value,
                                                step=1,
                                                precision=0,
                                                format="%.0f",
                                                value=line_item[j][k],
                                                on_change=lambda v,i=i,j=j,k=k: datadict[i][j].__setitem__(k, int(v.value)),
                                                ).style('width: 128px')
                with operation_bar().classes("baah-list-actions"):
                    ui.button(f"{config.get_text('button_add')} {linedesc[1]}", on_click=lambda i=i: add_item_item(i))
                    if len(datadict[i]) > 0:
                        ui.button(f"{config.get_text('button_delete')} {linedesc[1]}", on_click=lambda i=i: del_item_item(i), color="red")
        with form_row().classes("baah-list-items"):
            ui.button(f"{config.get_text('button_add')} {linedesc[0]}", on_click=add_item)
            if len(datadict) > 0:
                ui.button(f"{config.get_text('button_delete')} {linedesc[0]}", on_click=del_item, color="red")
 
    def add_item():
        datadict.append([])
        item_list.refresh()
    
    def del_item():
        datadict.pop()
        item_list.refresh()
        
    def get_num_of_last_item(mylist):
        """
        给定一个列表，返回最后一个元素的实际值
        
        如果该元素为number类型，返回number。如果该元素为list类型，返回list的第一个元素
        """
        if len(mylist) == 0:
            return 0
        item = mylist[-1]
        if isinstance(item, list) or isinstance(item, tuple):
            return item[0]
        else:
            return item
    
    def add_item_item(item_ind):
        if dim == 2: 
            if has_switch:
                # 有单个元素的开关的话，升维
                datadict[item_ind].append([int(get_num_of_last_item(datadict[item_ind]) + 1), True])
            else:
                datadict[item_ind].append(int(get_num_of_last_item(datadict[item_ind]) + 1))
        elif dim == 3:
            sublist = [1 for _ in range(subdim)]
            if has_switch:
                sublist.append(True)
            datadict[item_ind].append(sublist)
            # if subdim == 2:
            #     if has_switch:
            #         datadict[item_ind].append([1, 1, True])
            #     else:
            #         datadict[item_ind].append([1, 1])
            # elif subdim == 3:
            #     if has_switch:
            #         datadict[item_ind].append([1, 1, 1, True])
            #     else:
            #         datadict[item_ind].append([1, 1, 1])
        
        item_list.refresh()
    
    def del_item_item(item_ind):
        datadict[item_ind].pop()
        item_list.refresh()

    item_list()