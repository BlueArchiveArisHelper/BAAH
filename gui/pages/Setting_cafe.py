from nicegui import ui

def invite_seq_label(config, cafe_no, after_ticket=False):
    """
    Build the label of a cafe's invite number field.

    Args:
        config: the config whose language pack to read.
        cafe_no: the cafe number, 1 or 2.
        after_ticket: True for the field used after buying a ticket.

    Returns:
        The full sentence when the language pack has one, else the old joined label (zh/jp have no sentence key yet).
    """
    key = "cafe_buy_invite_seq" if after_ticket else "cafe_invite_seq"
    if config.has_text(key):
        return config.get_text(key).format(cafe_no)
    prefix = config.get_text("buy_ticket") if after_ticket else ""
    return f'{prefix}{cafe_no}{config.get_text("cafe_invite_desc")}'

def set_cafe(config):
    # 收集
    with ui.row():
        ui.checkbox(config.get_text("cafe_collect_desc")).bind_value(config.userconfigdict, "CAFE_COLLECT")
    
    # 摸头
    with ui.row():
        ui.checkbox(config.get_text("cafe_touch_desc")).bind_value(config.userconfigdict, "CAFE_TOUCH")
        ui.checkbox(config.get_text("enable_diff_touch")).bind_value(config.userconfigdict, "CAFE_TOUCH_WAY_DIFF").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
        
    ui.label(config.get_text("desc_cafe_invite"))

    with ui.row().bind_visibility_from(config.userconfigdict, "CAFE_TOUCH"):
        # 一号咖啡馆邀请+买票+邀请
        ui.number(invite_seq_label(config, 1), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, "CAFE1_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short")
        ui.checkbox(config.get_text("buy_ticket")).bind_value(config.userconfigdict, "CAFE1_BUY_INVITE_TICKET")
        ui.number(invite_seq_label(config, 1, after_ticket=True), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, "CAFE1_BUY_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short")

    
    with ui.row().bind_visibility_from(config.userconfigdict, "CAFE_TOUCH"):
        # 二号咖啡馆邀请+买票+邀请
        ui.number(invite_seq_label(config, 2), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, "CAFE2_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short")
        ui.checkbox(config.get_text("buy_ticket")).bind_value(config.userconfigdict, "CAFE2_BUY_INVITE_TICKET")
        ui.number(invite_seq_label(config, 2, after_ticket=True), min=0, max=5, precision=0, step=1).bind_value(config.userconfigdict, "CAFE2_BUY_INVITE_SEQ", forward=lambda x:int(x), backward=lambda x: int(x)).classes("baah-w-short")

    with ui.row().bind_visibility_from(config.userconfigdict, "CAFE_TOUCH"):
        ui.checkbox(config.get_text("config_cafe_samename_defer")).bind_value(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY")
        ui.checkbox(config.get_text("config_reversed")).bind_value(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY_REVERSE").bind_visibility_from(config.userconfigdict, "CAFE_INVITE_SAME_NAME_DELAY")


    # 关于视角的提示
    ui.label(config.get_text("config_cafe_attention"))
    full_camera = ui.checkbox(config.get_text("config_camera_full")).bind_value(config.userconfigdict, "CAFE_CAMERA_FULL").bind_visibility_from(config.userconfigdict, "CAFE_TOUCH")
    full_camera.set_value(True)
    full_camera.set_enabled(False)