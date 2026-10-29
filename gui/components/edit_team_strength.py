from nicegui import ui
from .modern_ui import form_row

def edit_the_team_strength_of_this_config(inconfig, affect_key):
    # 拿到这个config的key对应数据
    # [{"red":10, "blue":10, "yellow":10, "purple":10},
    #  {"red":10, "blue":10, "yellow":10, "purple":10},
    #  {"red":10, "blue":10, "yellow":10, "purple":10},
    #  {"red":0, "blue":0, "yellow":0, "purple":0}]
    strength_list = inconfig.userconfigdict[affect_key]
    color_list = ["red", "blue", "yellow", "purple"]
    # 如果长度不为4，补充至4
    while len(strength_list) < 4:
        strength_list.append({color: 0 for color in color_list})
    strength_list = strength_list[:4]
    for i in range(4):
        ui.label(f"队伍 {i+1} : ")
        # 队伍字段自动换行，保留原有强度范围与绑定。
        with form_row().classes("baah-team-row"):
            for cind, color in enumerate(color_list):
                ui.number(inconfig.get_text("team_"+color_list[cind]), min=0, max=10).bind_value(strength_list[i], color, forward=lambda x: int(x), backward=lambda x: int(x))
        