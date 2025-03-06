# 一个用户config的GUI显示
from nicegui import ui, run
import requests

import os
from gui.components.run_baah_in_gui import run_baah_task
from gui.pages.Setting_BAAH import set_BAAH
from gui.pages.Setting_cafe import set_cafe
from gui.pages.Setting_emulator import set_emulator
from gui.pages.Setting_event import set_event
from gui.pages.Setting_exchange import set_exchange
from gui.pages.Setting_hard import set_hard
from gui.pages.Setting_normal import set_normal
from gui.pages.Setting_other import set_other
from gui.pages.Setting_server import set_server
from gui.pages.Setting_shop import set_shop
from gui.pages.Setting_special import set_special
from gui.pages.Setting_task_order import set_task_order
from gui.pages.Setting_timetable import set_timetable
from gui.pages.Setting_wanted import set_wanted
from gui.pages.Setting_notification import set_notification
from gui.pages.Setting_vpn import set_vpn
from gui.pages.Setting_Assault import set_assault
from gui.pages.Setting_BuyAP import set_buyAP



@ui.refreshable
def show_GUI(load_jsonname, config, shared_softwareconfig):
    
    # 如果是example.json，则大字提醒
    if load_jsonname == "example.json":
        ui.label(config.get_text("notice_example_json")).style("font-size: 30px; color: red;")
        
    config.parse_user_config(load_jsonname)

    # myAllTask里面的key与GUI显示的key的映射
    real_taskname_to_show_taskname = {
        "登录游戏":config.get_text("task_login_game"),
        "清momotalk":config.get_text("task_clear_momotalk"),
        "咖啡馆":config.get_text("task_cafe"),
        "咖啡馆只摸头":config.get_text("task_cafe_deprecated"), # 为了兼容以前的配置里的咖啡馆只摸头，这里只改显示名
        "课程表":config.get_text("task_timetable"),
        "社团":config.get_text("task_club"),
        "商店":config.get_text("task_shop"),
        "购买AP":config.get_text("task_buy_ap"),
        "悬赏通缉":config.get_text("task_wanted"),
        "特殊任务":config.get_text("task_special"),
        "学园交流会":config.get_text("task_exchange"),
        "战术大赛":config.get_text("task_contest"),
        "战术大赛只领奖":config.get_text("task_contest_only_reward"),
        "困难关卡":config.get_text("task_hard"),
        "活动关卡":config.get_text("task_event"),
        "总力战":config.get_text("task_assault"),
        "每日任务":config.get_text("task_daily"),
        "邮件":config.get_text("task_mail"),
        "普通关卡":config.get_text("task_normal"),
        "普通推图":config.get_text("push_normal"),
        "困难推图":config.get_text("push_hard"),
        "主线剧情":config.get_text("push_main_story"),
    }

    # =============================================

    # =============================================

    with ui.row().style('min-width: 800px; display: flex; flex-direction: row;flex-wrap: nowrap;'):
        with ui.column().style('height:80vh;min-width: 200px; width: 10vw; overflow: auto;flex-grow: 1; position: sticky; top: 0px;'):
            with ui.card().style('overflow: auto;'):
                ui.link("BAAH", '#BAAH')
                ui.link(config.get_text("setting_emulator"), '#EMULATOR')
                ui.link(config.get_text("setting_server"), '#SERVER')
                ui.link(config.get_text("setting_vpn"), '#VPN')
                ui.link(config.get_text("setting_task_order"), '#TASK_ORDER')
                ui.link(config.get_text("setting_notification"), '#NOTIFICATION')
                # ui.link(config.get_text("setting_next_config"), '#NEXT_CONFIG')
                ui.link(config.get_text("task_cafe"), '#CAFE')
                ui.link(config.get_text("task_timetable"), '#TIME_TABLE')
                ui.link(config.get_text("task_shop"), '#SHOP_NORMAL')
                ui.link(config.get_text("task_buy_ap"), '#BUY_AP')
                ui.link(config.get_text("task_wanted"), '#WANTED')
                ui.link(config.get_text("task_special"), '#SPECIAL_TASK')
                ui.link(config.get_text("task_exchange"), '#EXCHANGE')
                ui.link(config.get_text("task_event"), '#ACTIVITY')
                ui.link(config.get_text("task_assault"), '#ASSAULT')
                ui.link(config.get_text("task_hard"), '#HARD')
                ui.link(config.get_text("task_normal"), '#NORMAL')
                ui.link(config.get_text("setting_other"), '#TOOL_PATH')


        with ui.column().style('flex-grow: 4; width: 50vw;'):
            
            set_BAAH(config, shared_softwareconfig)
            
            # 模拟器配置
            set_emulator(config)
            
            # 服务器配置
            set_server(config)
            
            # 自己的加速器配置
            set_vpn(config)
            
            # 任务执行顺序，后续配置文件
            set_task_order(config, real_taskname_to_show_taskname)
            
            # 通知
            set_notification(config, shared_softwareconfig)
            
            # 咖啡馆
            set_cafe(config)
            
            # 课程表
            set_timetable(config)
                
            # 商店
            set_shop(config)
            
            # 购买AP
            set_buyAP(config)
            
            # 悬赏通缉
            set_wanted(config)
            
            # 特殊任务
            set_special(config)
            
            # 学园交流会
            set_exchange(config)

            # 活动关卡
            set_event(config)
            
            # 总力战
            set_assault(config)
                
            # 困难关卡
            set_hard(config)
            
            # 普通关卡
            set_normal(config)
            
            # 其他设置
            set_other(config, load_jsonname)

        msg_obj = {
            "msg": "",
            "stop_signal": 0,
            "runing_signal": 0
        }
        
        @ui.refreshable
        def output_area():
            with ui.column().style('flex-grow: 1;width: 30vw;position:sticky; top: 0px;'):
                with ui.card().style('width: 30vw; height: 80vh;overflow-y: auto;'):
                    ui.html(f'<span>{msg_obj.get("msg", "")}</span>')
        output_area()
        
        with ui.column().style('width: 10vw; overflow: auto; position: fixed; bottom: 40px; right: 20px;min-width: 150px;'):
            
            def save_and_alert():
                config.save_user_config(load_jsonname)
                config.save_software_config()
                shared_softwareconfig.save_software_config()
                ui.notify(config.get_text("notice_save_success"))
            ui.button(config.get_text("button_save"), on_click=save_and_alert)

            async def save_and_alert_and_run():
                config.save_user_config(load_jsonname)
                config.save_software_config()
                shared_softwareconfig.save_software_config()
                ui.notify(config.get_text("notice_save_success"))
                ui.notify(config.get_text("notice_start_run"))
                # 打开同目录中的BAAH.exe，传入当前config的json文件名
                # os.system(f'start BAAH.exe "{load_jsonname}"')
                msg_obj["runing_signal"] = 1
                await run.io_bound(run_baah_task, msg_obj, output_area, config)
            ui.button(config.get_text("button_save_and_run"), on_click=save_and_alert_and_run).bind_visibility_from(msg_obj, "runing_signal", backward=lambda x:x == 0)
            
            async def stop_run() -> None:
                msg_obj["stop_signal"] = 1
            ui.button(config.get_text("notice_finish_run"), on_click=stop_run, color='red').bind_visibility_from(msg_obj, "runing_signal", backward=lambda x:x == 1)
            
            ui.button("...").bind_visibility_from(msg_obj, "runing_signal", backward=lambda x:x == 0.25)
        
    # 加载完毕保存一下config，应用最新的对config的更改
    config.save_user_config(load_jsonname)
    config.save_software_config()