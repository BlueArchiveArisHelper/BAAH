from nicegui import ui

from gui.components.plot_source_line import create_line_chart
from modules.utils import _is_PC_app


def set_BAAH(config, shared_softwareconfig):
    
    with ui.column():
        ui.link_target("BAAH")
        ui.label(f"Blue Archive Aris Helper {config.NOWVERSION} ==> ({config.nowuserconfigname})").style('font-size: xx-large')

        # ui.label(config.get_text("BAAH_desc"))
        
        web_url = {
                    "github": "https://github.com/sanmusen214/BAAH",
                    "bilibili":"https://space.bilibili.com/7331920"
                }
        
        with ui.row():
            ui.link("Github", web_url["github"], new_tab=True)
            ui.link("Bilibili", web_url["bilibili"], new_tab=True)

        with ui.row():
            ui.label(config.get_text("BAAH_attention")).style('color: red; font-size: x-large')
            ui.label(f'  {config.get_text("notice_steam_esc_break")}').style('color: red; font-size: x-large').bind_visibility_from(config.userconfigdict, "SERVER_TYPE", backward=lambda x: _is_PC_app(x))

        # kei的教程
        with ui.row():
            ui.link("BV1ZxfGYSEVr", "https://www.bilibili.com/video/BV1ZxfGYSEVr/", new_tab=True)
            ui.html('<iframe  src="//www.bilibili.com/blackboard/html5mobileplayer.html?aid=113877383648785&bvid=BV1ZxfGYSEVr&cid=28301724347&p=1" width="360px" height="240px" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>', sanitize=False)

        # ui.link("BV1ZxfGYSEVr", "https://www.bilibili.com/video/BV1pi4y1W7QB/", new_tab=True)
        # ui.html('<iframe  src="//www.bilibili.com/blackboard/html5mobileplayer.html?aid=539065954&bvid=BV1pi4y1W7QB&cid=1413492023&p=1" width="720px" height="480px" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>', sanitize=False)

        # 记录的折线图
        create_line_chart(config.userstoragedict.get("HISTORY_MONEY_DIAMOND_LIST", []))