from nicegui import ui
from modules.utils import encrypt_data, decrypt_data

def set_notification(config, shared_softwareconfig):
    with ui.row():
        ui.link_target("NOTIFICATION")
        ui.label(config.get_text("setting_notification")).style('font-size: x-large')
    
    with ui.card():
        ui.checkbox(config.get_text("desc_noti_when_success")).bind_value(config.userconfigdict, "NOTI_WHEN_SUCCESS")
        ui.checkbox(config.get_text("desc_noti_when_error")).bind_value(config.userconfigdict, "NOTI_WHEN_ERROR")

    with ui.row():

        # 邮件
        with ui.card():
            ui.checkbox(config.get_text("email_notification_desc")).bind_value(config.userconfigdict, 'ENABLE_MAIL_NOTI')
            ui.input(config.get_text("email_account")).bind_value(config.userconfigdict, "MAIL_USER").style("width: 300px")
            ui.input(config.get_text("email_pwd"), password=True, password_toggle_button=True).bind_value(
                config.userconfigdict, 
                "MAIL_PASS", 
                forward= lambda x: encrypt_data(x, shared_softwareconfig.softwareconfigdict["ENCRYPT_KEY"]),
                backward= lambda x: decrypt_data(x, shared_softwareconfig.softwareconfigdict["ENCRYPT_KEY"])
                ).style("width: 300px")
            
            # 高级模式让用户自己选择邮件发送服务器
            ui.checkbox(config.get_text("config_email_advaned")).bind_value(config.userconfigdict, "ADVANCED_EMAIL")
            
            with ui.row().bind_visibility_from(config.userconfigdict, "ADVANCED_EMAIL"):
                # 发件人
                ui.input(config.get_text("config_email_sender")).bind_value(config.userconfigdict, "SENDER_EMAIL").style("width: 300px")
                # 收件人
                ui.input(config.get_text("config_email_receiver")).bind_value(config.userconfigdict, "RECEIVER_EMAIL").style("width: 300px")
                # 邮件服务器
                ui.input(config.get_text("config_email_smtp")).bind_value(config.userconfigdict, "MAIL_HOST").style("width: 300px")

            ui.label(config.get_text("get_email_pwd"))
            ui.html('<iframe src="//player.bilibili.com/player.html?aid=583874363&bvid=BV16z4y1D74s&cid=211611094&p=1&autoplay=0" width="720px" height="480px" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>', sanitize=False)
        
        with ui.card():
            ui.checkbox(config.get_text("config_api_noti")).bind_value(config.userconfigdict, "ENABLE_HTTP_NOTI")
            ui.select({0: "GET", 1: "POST"}, label=config.get_text("config_api_noti_method")).bind_value(config.userconfigdict, "WEB_NOTI_TYPE_GET_OR_POST").style("width: 300px")
            ui.input(config.get_text("config_api_noti_token"),
                     password=True,
                     password_toggle_button=True
                     ).bind_value(config.userconfigdict, "TARGET_HTTP_TOKEN").style("width: 300px")
                
            # 目标url
            ui.label("Keywords: [token], [title], [content]")
            ui.input(config.get_text("config_api_noti_url")).bind_value(config.userconfigdict, "TARGET_HTTP_URL").style("width: 500px")
            with ui.column().bind_visibility_from(config.userconfigdict, "WEB_NOTI_TYPE_GET_OR_POST", backward=lambda x: x == 1):
                ui.label(config.get_text("config_api_noti_body_desc"))
                ui.textarea(label=config.get_text("config_api_noti_header"),
                                            placeholder='{"Content-Type": "application/json;charset=utf-8","Authorization": "[token]"}'
                                            ).bind_value(config.userconfigdict, "WEB_NOTI_POST_HEADER").style("width: 500px; height: 200px")
                ui.textarea(label=config.get_text("config_api_noti_body"),
                            placeholder='{"token": "[token]", "title": "[title]", "content": "[content]"}'
                            ).bind_value(config.userconfigdict, "WEB_NOTI_POST_CONTENT").style("width: 500px; height: 200px")
            
            # 渠道的自动填充地址与帮助地址共同维护，按钮和帮助图标成组排列。
            mapdict = {
                "PushPlus": {
                    "url": "http://www.pushplus.plus/send?token=[token]&title=[title]&content=[content]&template=txt",
                    "help_url": "http://www.pushplus.plus/",
                },
                "ServerChan": {
                    "url": "https://sctapi.ftqq.com/[token].send?title=[title]&desp=[content]",
                    "help_url": "https://sct.ftqq.com/r/13283",
                },
                "Telegram Bot": {
                    "url": "https://api.telegram.org/bot[token]/sendMessage?chat_id=[chat_id]&text=[content]",
                    "help_url": "https://t.me/BotFather",
                },
            }
            with ui.row():
                for name, channel in mapdict.items():
                    with ui.row().classes('items-center gap-1 flex-nowrap'):
                        ui.button(name, color=None, on_click=lambda name=name: set_api_noti_type(name))
                        with ui.link(target=channel['help_url'], new_tab=True).classes(
                            'inline-flex items-center justify-center p-1 rounded'
                        ).props(f'aria-label="{name}: {config.get_text("text_description")}" rel="noopener noreferrer"').tooltip(name):
                            ui.icon('info_outline').classes('text-lg')
            def set_api_noti_type(type):
                config.userconfigdict["TARGET_HTTP_URL"] = mapdict.get(type, {}).get("url", "")
                # 用户切换渠道，先只改url格式
                # config.userconfigdict["WEB_NOTI_TYPE_GET_OR_POST"] = 0
            
    
    # 说明与输入框保持同列，原有 placeholder 和配置绑定不变。
    with ui.column().classes('baah-described-field'):
        ui.label(config.get_text('desc_noti_content_diy_hint')).classes('baah-help-text')
        ui.textarea(placeholder=config.get_text("desc_noti_content_diy")).bind_value(config.userconfigdict, "CUSTOM_EMAIL").style("width: 500px; height: 200px")
