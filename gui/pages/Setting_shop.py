from nicegui import ui
from gui.components.list_edit_area import list_edit_area
from gui.components.modern_ui import info_tip

def refresh_field(config, shop):
    """
    Build a shop's refresh count field, with a tooltip that names what each refresh costs.

    Args:
        config: the config to edit.
        shop: `normal` or `contest`. zh/jp have no short label key yet, so they keep the old label built from the shop name.
    """
    with info_tip(config, f"tip_shop_{shop}_refresh"):
        ui.number(
                config.get_text("config_shop_refreshes"),
                step=1,
                precision=0,
                min=0,
                max=3
                ).bind_value(config.userconfigdict, f'SHOP_{shop.upper()}_REFRESH_TIME', forward=lambda v: int(v)).classes("baah-w-short")

def set_shop(config):
    with ui.row():
        ui.link_target("SHOP_NORMAL")
        ui.label(config.get_text("config_shop_normal")).style('font-size: x-large')
        # 开关
        ui.switch(config.get_text("config_shop_normal_switch")).bind_value(config.userconfigdict, "SHOP_NORMAL_SWITCH")    
    
    with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_NORMAL_SWITCH"):
        refresh_field(config, "normal")

        # 购买所有
        ui.checkbox(config.get_text("config_shop_normal_buyall")).bind_value(config.userconfigdict, "SHOP_NORMAL_BUYALL").style("color: red")

        with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_NORMAL_BUYALL", lambda v: not v):
            list_edit_area(config.userconfigdict["SHOP_NORMAL"], [config.get_text("config_row"), config.get_text("config_column")], config.get_text("config_desc_shop_edit"), has_switch=True)
    
    with ui.row():
        ui.link_target("SHOPCONTEST")
        ui.label(config.get_text("config_shop_contest")).style('font-size: x-large')
        # 开关
        ui.switch(config.get_text("config_shop_contest_switch")).bind_value(config.userconfigdict, "SHOP_CONTEST_SWITCH") 

    with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_CONTEST_SWITCH"):
        refresh_field(config, "contest")

        # 购买所有
        ui.checkbox(config.get_text("config_shop_contest_buyall")).bind_value(config.userconfigdict, "SHOP_CONTEST_BUYALL").style("color: red")

        with ui.column().bind_visibility_from(config.userconfigdict, "SHOP_CONTEST_BUYALL", lambda v: not v):
            list_edit_area(config.userconfigdict["SHOP_CONTEST"], [config.get_text("config_row"), config.get_text("config_column")], config.get_text("config_desc_shop_edit"), has_switch=True)