from nicegui import ui
from gui.components.modern_ui import setting_group, form_grid, info_tip, notice_box

def invite_seq_label(config, cafe_no, after_ticket=False):
    """
    Build the label of a cafe's invite number field.

    Args:
        config: the config whose language pack to read.
        cafe_no: the cafe number, 1 or 2.
        after_ticket: True for the field used after buying a ticket.

    Returns:
        The short label used inside the cafe's card, else the old joined label (zh/jp have no short key yet).
    """
    key = "cafe_buy_invite_seq" if after_ticket else "cafe_invite_seq"
    return config.get_text(key)

def cafe_card(config, cafe_no):
    """
    Build one cafe's invite settings in a card titled with the cafe's number.

    Args:
        config: the config to edit.
        cafe_no: the cafe number, 1 or 2.
    """
    cafe_no = int(cafe_no)
    with setting_group(f'{config.get_text("task_cafe")} {cafe_no}'):
        with info_tip(config, "tip_cafe_invite_seq"):
            ui.number(invite_seq_label(config, cafe_no), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, f"CAFE{cafe_no}_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short")
        ui.checkbox(config.get_text("buy_ticket")).bind_value(config.userconfigdict, f"CAFE{cafe_no}_BUY_INVITE_TICKET")
        ui.number(invite_seq_label(config, cafe_no, after_ticket=True), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, f"CAFE{cafe_no}_BUY_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short").bind_visibility_from(config.userconfigdict, f"CAFE{cafe_no}_BUY_INVITE_TICKET")

def set_cafe(config):
    # 收集
    with ui.row():
        ui.checkbox(config.get_text("cafe_collect_desc")).bind_value(config.userconfigdict, "CAFE_COLLECT")
    
    # 摸头
    with ui.row():
        ui.checkbox(config.get_text("cafe_touch_desc")).bind_value(config.userconfigdict, "CAFE_TOUCH")
        ui.checkbox(config.get_text("enable_diff_touch")).bind_value(config.userconfigdict, "CAFE_TOUCH_WAY_DIFF").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        
    ui.label(config.get_text("desc_cafe_invite"))

    # 每个咖啡馆一张卡片：邀请+买票+邀请
    with form_grid().bind_visibility_from(config.userconfigdict, "CAFE_TOUCH"):
        cafe_card(config, 1)
        cafe_card(config, 2)

    with ui.row().bind_visibility_from(config.userconfigdict, "CAFE_TOUCH"):
        ui.checkbox(config.get_text("config_cafe_samename_defer")).bind_value(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY")
        ui.checkbox(config.get_text("config_reversed")).bind_value(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY_REVERSE").bind_visibility_from(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY")


    # 关于视角的提示
    notice_box(config.get_text("config_cafe_attention"))
    # Touching assumes the widest camera view and never pans, so the page keeps it on as before; the old checkbox was always on and disabled
    config.userconfigdict["CAFE_CAMERA_FULL"] = True