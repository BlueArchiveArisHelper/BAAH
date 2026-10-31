from nicegui import ui
from gui.components.modern_ui import notice_box

def set_buyAP(config):
    # 购买判断与单价风险仅增加提醒，不更改购买规则或数值约束。
    notice_box(config.get_text("config_buy_ap_rules_notice"), tone="warning")
    with ui.card():
        ui.label(config.get_text("config_buy_ap_attention"))
        ui.number(config.get_text("config_buy_ap_max_price"), min=0, precision=0, step=30).bind_value(config.userconfigdict, "BUY_AP_MAX_PRICE", forward= lambda x: int(x)).classes("baah-w-short")
        ui.number(config.get_text("config_buy_ap_add_times"), min=0, precision=0, step=1).bind_value(config.userconfigdict, "BUY_AP_ADD_TIMES", forward= lambda x: int(x)).classes("baah-w-short")