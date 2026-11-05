import time
from nicegui import ui
from .modern_ui import form_row, surface, operation_bar, notice_box, info_tip, confirm_delete
from modules.configs.MyConfig import config
from modules.utils.data_utils import day_plan_index

def ordinal(n):
    # 1st, 2nd, 3rd, 4th ... 11th, 12th, 13th ... 21st
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def run_dates(i, n):
    # Plan `i` runs on these dates of the month, picked the same way as the tasks do
    return [d for d in range(1, 32) if day_plan_index(d, n) == i]

def runs_text(dates):
    """
    Say on which dates of the month a day plan runs.

    Args:
        dates: the dates from `run_dates`.

    Returns:
        The sentence, or "" when the language pack has no text for it.
    """
    if len(dates) == 31:
        key = "config_runs_every_day"
    elif not dates:
        key = "config_runs_never"
    else:
        key = "config_runs_on"
    if not config.has_text(key):
        return ""
    more = " \u2026" if len(dates) > 3 else ""
    return config.get_text(key).format(dates=", ".join(map(ordinal, dates[:3])) + more)

def list_edit_area(datadict, linedesc, blockdesc="", has_switch=False, 
                   min_value_for_1st_dim = 1,min_value_for_2nd_dim = 1, min_value_for_3rd_dim = -99, *, blockdesc_as_notice=False, empty_line_prompt_id="config_no_data_set_here",
                   column_tips=()):
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
    column_tips: i18n keys of the tooltips for the column names in `linedesc[2]`, one per column. A missing key shows no icon.
    """
    dim = len(linedesc)
    # 对列表的最后一维的元素的文字描述的数量
    # [关卡，次数] -> subdim = 2 = len(linedesc[2])
    # [地区，关卡，次数] -> subdim = 3 = len(linedesc[2])
    subdim = 0
    if dim >= 3:
        subdim = len(linedesc[2])

    def heading(i):
        # en_US reads "Day 1". zh/jp have no template yet, so they keep the old "第 1 天: " order.
        if config.has_text("config_nth_heading"):
            return config.get_text("config_nth_heading").format(item=linedesc[0], n=i+1)
        return f'{config.get_text("config_nth")} {i+1} {linedesc[0]}: '

    def min_value_of(k):
        # 最后一列是扫荡次数，倒数第二列是关卡序号，其余（地区序号）用第一维的最小值
        if k == subdim-1:
            return min_value_for_3rd_dim
        if k == subdim-2:
            return min_value_for_2nd_dim
        return min_value_for_1st_dim

    def set_switch(row, value):
        # Sets the switch, or adds it to a stage that an old config saved without one
        row[subdim:] = [value]

    def day_card(i):
        """
        Show one day as a card: the column names once, then one row of inputs per stage.

        Args:
            i: the index of the day in `datadict`.
        """
        line_item = datadict[i]
        title = heading(i)
        dates = run_dates(i, len(datadict))
        runs = runs_text(dates)
        is_today = config.has_text("config_today") and time.localtime().tm_mday in dates
        with surface("baah-day-card" + (" baah-day-today" if is_today else "")):
            with ui.row(wrap=False).classes("baah-title-row"):
                with ui.row().classes("baah-day-head"):
                    ui.label(title).classes("baah-group-title")
                    if runs:
                        ui.label(runs).classes("baah-day-runs baah-muted")
                    if is_today:
                        ui.badge(config.get_text("config_today")).props("rounded")
                with ui.button(icon="delete_outline", on_click=lambda: ask_del_day(i, title), color=None).props("flat round dense"):
                    ui.tooltip(config.get_text("tip_remove_day").format(day=title))
            if len(line_item) == 0:
                notice_box(config.get_text(empty_line_prompt_id), tone="warning")
            else:
                # 最后一列放每个关卡的删除按钮
                columns = f"repeat({subdim}, 112px)" + (" auto" if has_switch else "") + " auto"
                with ui.element("div").classes("baah-day-grid").style(f"grid-template-columns: {columns}"):
                    for k in range(subdim):
                        with info_tip(config, column_tips[k] if k < len(column_tips) else None):
                            ui.label(linedesc[2][k]).classes("baah-day-column baah-muted")
                    if has_switch:
                        ui.label(config.get_text("config_switch_column")).classes("baah-day-column baah-muted")
                    ui.element("div")
                    for j, row in enumerate(line_item):
                        for k in range(subdim):
                            ui.number(min=min_value_of(k),
                                      step=1,
                                      precision=0,
                                      format="%.0f",
                                      value=row[k],
                                      on_change=lambda v,row=row,k=k: row.__setitem__(k, int(v.value)),
                                      )
                        if has_switch:
                            # BAAH runs a stage that has no switch, so an empty slice shows as ticked
                            ui.checkbox(value=all(row[subdim:]), on_change=lambda v,row=row: set_switch(row, bool(v.value)))
                        with ui.button(icon="remove_circle_outline", on_click=lambda j=j: del_item_item(i, j), color="red").props("flat round dense"):
                            ui.tooltip(config.get_text("tip_remove_stage"))
            ui.button(config.get_text("button_add_stage"), icon="add", on_click=lambda: add_item_item(i)).props("flat")

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
            if dim == 3:
                day_card(i)
                continue
            line_item = datadict[i]
            ui.label(heading(i))
            with form_row().classes("baah-list-items"):
                if len(line_item) == 0:
                    notice_box(config.get_text(empty_line_prompt_id), tone="warning")
                for j in range(len(line_item)):
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
                                with form_row():
                                    ui.checkbox(value=line_item[j][1],on_change=lambda v,i=i,j=j:datadict[i][j].__setitem__(1, bool(v.value)))
                                    ui.label(config.get_text("button_enable"))
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
                with operation_bar().classes("baah-list-actions"):
                    ui.button(f"{config.get_text('button_add')} {linedesc[1]}", on_click=lambda i=i: add_item_item(i))
                    if len(datadict[i]) > 0:
                        ui.button(f"{config.get_text('button_delete')} {linedesc[1]}", on_click=lambda i=i: del_item_item(i, -1), color="red")
        with form_row().classes("baah-list-items"):
            if dim == 3:
                # Each day card has its own remove button, so only Add stays here
                add_day = config.get_text("button_add_day") if config.has_text("button_add_day") else f"{config.get_text('button_add')} {linedesc[0]}"
                ui.button(add_day, icon="add", on_click=add_item).props("outline")
            else:
                ui.button(f"{config.get_text('button_add')} {linedesc[0]}", on_click=add_item)
                if len(datadict) > 0:
                    ui.button(f"{config.get_text('button_delete')} {linedesc[0]}", on_click=lambda: del_item(-1), color="red")
 
    def add_item():
        datadict.append([])
        item_list.refresh()
    
    def del_item(item_ind):
        datadict.pop(item_ind)
        item_list.refresh()

    def ask_del_day(i, title):
        # An empty last day loses nothing, since Add day brings it back as it was
        body_ids = []
        if datadict[i]:
            body_ids.append("confirm_delete_day_stages")
        if i < len(datadict) - 1:
            body_ids.append("confirm_delete_day_shift")
        if not body_ids:
            return del_item(i)
        return confirm_delete(config, lambda: del_item(i), "confirm_delete_day", *body_ids, day=title, stages=len(datadict[i]))
        
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
    
    def del_item_item(item_ind, sub_ind):
        datadict[item_ind].pop(sub_ind)
        item_list.refresh()

    item_list()