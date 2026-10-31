from nicegui import ui
from gui.components.list_edit_area import list_edit_area

def set_shop(config):
    with ui.row():
        ui.link_target("SHOP_NORMAL")
        ui.label(config.get_text("config_shop_normal")).style('font-size: x-large')
        # 开关
        ui.switch(config.get_text("config_shop_normal_switch")).bind_value(config.userconfigdict, "SHOP_NORMAL_SWITCH")    
    
    ui.number(
            f'{config.get_text("config_shop_normal")} {config.get_text("config_refresh")} {config.get_text("config_times")}',
            step=1,
            precision=0,
            min=0,
            max=3
            ).bind_value(config.userconfigdict, 'SHOP_NORMAL_REFRESH_TIME', forward=lambda v: int(v)).classes("baah-w-short")
    
    # 购买所有
    ui.checkbox(config.get_text("config_shop_normal_buyall")).bind_value(config.userconfigdict, "SHOP_NORMAL_BUYALL").style("color: red")

    with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_NORMAL_BUYALL", lambda v: not v):
        list_edit_area(config.userconfigdict["SHOP_NORMAL"], [config.get_text("config_row"), config.get_text("config_column")], config.get_text("config_desc_shop_edit"), has_switch=True)
    
    with ui.row():
        ui.link_target("SHOPCONTEST")
        ui.label(config.get_text("config_shop_contest")).style('font-size: x-large')
        # 开关
        ui.switch(config.get_text("config_shop_contest_switch")).bind_value(config.userconfigdict, "SHOP_CONTEST_SWITCH") 

    ui.number(
            f'{config.get_text("config_shop_contest")} {config.get_text("config_refresh")} {config.get_text("config_times")}',
            step=1,
            precision=0,
            min=0,
            max=3
            ).bind_value(config.userconfigdict, 'SHOP_CONTEST_REFRESH_TIME', forward=lambda v: int(v)).classes("baah-w-short")
    

    # 购买所有
    ui.checkbox(config.get_text("config_shop_contest_buyall")).bind_value(config.userconfigdict, "SHOP_CONTEST_BUYALL").style("color: red")

    with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_CONTEST_BUYALL", lambda v: not v):
        list_edit_area(config.userconfigdict["SHOP_CONTEST"], [config.get_text("config_row"), config.get_text("config_column")], config.get_text("config_desc_shop_edit"), has_switch=True)