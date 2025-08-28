from nicegui import ui
from modules.configs.settingMaps import server2pic, server2activity, server2respond

def set_server(config):
    with ui.row():
        ui.link_target("SERVER")
        ui.label(config.get_text("setting_server")).style('font-size: x-large')
    
    server = ui.radio({
        "JP":config.get_text("config_server_jp"), 
        "GLOBAL":config.get_text("config_server_global"), 
        "GLOBAL_EN":config.get_text("config_server_global_en"),
        "CN":config.get_text("config_server_cn"),
        "CN_BILI":config.get_text("config_server_cn_b")},
                      value=config.userconfigdict['SERVER_TYPE'], on_change=lambda a:set_server_info(a.value)).props('inline')
    
    def set_server_info(servername):
        config.userconfigdict['SERVER_TYPE'] = servername
        config.userconfigdict["PIC_PATH"] = server2pic[servername]
        config.userconfigdict["ACTIVITY_PATH"] = server2activity[servername]
        if config.userconfigdict["LOCK_SERVER_TO_RESPOND_Y"]:
            config.userconfigdict["RESPOND_Y"] = server2respond[servername]
    
    #  大更新配置
    #  BlockHaity:没写逻辑，先隐藏
    ui.checkbox(config.get_text("config_big_update")).bind_value(config.userconfigdict, "BIG_UPDATE")
    
    ui.label(config.get_text("big_update_type")).style('font-size: large').bind_visibility_from(config.userconfigdict, "BIG_UPDATE", lambda x: x)
    
    ui.radio({
        "API":config.get_text("big_update_type_api"),
        "DIRECT_GET":config.get_text("big_update_type_direct_get")
    },
                    value=config.userconfigdict['BIG_UPDATE_TYPE'], on_change=lambda a:set_big_update_type(a.value)).props('inline').bind_visibility_from(config.userconfigdict, "BIG_UPDATE", lambda x: x)
    
    ui.label(config.get_text("big_update_type_direct_get_tips")).bind_visibility_from(config.userconfigdict, "BIG_UPDATE_TYPE", lambda x: x == "DIRECT_GET")
    
    def set_big_update_type(big_update_type):
        config.userconfigdict['BIG_UPDATE_TYPE'] = big_update_type