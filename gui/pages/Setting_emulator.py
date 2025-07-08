from nicegui import ui, run
from modules.utils import check_connect, connect_to_device


def set_emulator(config):
    
    # def noti_user(res):
    #     ui.notify(res)
    #     if res == NO_NEED:
    #         ui.notify(istr({CN:"无需操作", EN:"No need to operate", JP:"操作不要"}))
    #     elif res == ERROR:
    #         # ui.notify("操作失败。请检查所需条件，查看命令窗口报错")
    #         ui.notify(istr({CN:"操作失败。请检查所需条件，查看命令窗口报错", EN:"Operation failed. Please check the required conditions and view the command window error", JP:"操作に失敗しました。必要な条件を確認し、コマンドウィンドウのエラーを表示してください"}))
    #     elif res == FAILED:
    #         ui.notify(istr({CN:"操作失败，检查设置", EN:"Operation failed, check settings", JP:"操作に失敗しました, 設定を確認してください"}))
    #     elif res == SUCCESS:
    #         ui.notify(istr({CN:"操作成功", EN:"Operation successful", JP:"操作は成功しました"}))
    #     elif res == NO_FILE:
    #         ui.notify(istr({CN:"未找到文件", EN:"File not found", JP:"ファイルが見つかりません"}))
    #     else:
    #         ui.notify(istr({CN:"未知错误", EN:"Unknown error", JP:"不明なエラー"}))
    
    # async def fix_mumu_jp_server(cfig):
    #     """修复MUMU模拟器日服无法登录问题"""
    #     ui.notify(ui.notify(istr({CN:"运行中...", EN:"Running...", JP:"実行中..."})))
    #     connect_to_device(cfig)
    #     res = await run.io_bound(mumu_rm_mu, cfig)
    #     noti_user(res)
    
    
    ui.link_target("EMULATOR")
    ui.label(config.get_text("setting_emulator")).style('font-size: x-large')
    
    
    # with ui.row().bind_visibility_from(config.userconfigdict, "TARGET_PORT", lambda v: v>=16384):
    #     with ui.card():
    #         ui.label(istr({CN:"修复MUMU模拟器日服无法登录问题", EN:"FIX MUMU JP Server Login Issue", JP:"MUMUエミュレータの日本サーバーへのログイン問題を修正"})).style('font-size: large')
    #         ui.label(istr({CN:"修复前请手动设置以下内容，修复中遇到弹窗请点击 允许", EN:"Before fixing, please manually set the following content. If you encounter a pop-up window during the repair, please click Allow,Settings:", JP:"修正前に以下の内容を手動で設定してください。修正中にポップアップウィンドウが表示された場合は、許可をクリックしてください："}))
    #         ui.label(istr({CN:"1. 设置-其他-开启手机ROOT权限", EN:"1. Settings-Other-Enable phone ROOT permission", JP:"1. 設定-その他-携帯電話のROOT権限を有効にする"}))
    #         ui.label(istr({CN:"2. 设置-磁盘-磁盘共享-可写系统盘 (重启)", EN:"2. Settings-Disk-Disk Sharing-Writable System Disk (Restart)", JP:"2. 設定-ディスク-ディスク共有-書き込み可能なシステムディスク（再起動）"}))
    #         ui.label(istr({CN:"本操作不可逆！此端口模拟器将会丢失ROOT权限", 
    #                        EN:"This operation is irreversible! This emulator will lose ROOT permission",
    #                         JP:"この操作は取り消しできません！このエミュレータはROOT権限を失います"})).style('color: red')
    #         clickonce = {"click":0}
    #         with ui.row():
    #             ui.button(istr({CN:"修复", EN:"Fix", JP:"修正"}), on_click=lambda c=clickonce: c.update({"click":1}), color="warning").bind_visibility_from(clickonce, "click", lambda v: v==0)
    #             ui.button(istr({CN:"再次点击进行修复", EN:"Click again to Fix", JP:"再度クリックして修正"}), on_click=lambda c=config:fix_mumu_jp_server(c)).bind_visibility_from(clickonce, "click", lambda v: v>=1)
    #         with ui.row():
    #             ui.label(istr({CN:"修复后请直接重开模拟器", EN:"Please restart the emulator directly after fixing", JP:"修正後、直接エミュレータを再起動してください"}))
    #             ui.label(istr({CN:"请勿再次更改上面设置, 否则修复失效", EN:"Do not change the above settings again, or fix will be disabled", JP:"上記の設定を再度変更しないでください。さもないと修正が無効になります"})).style('color: red')

    with ui.row():
        # IP+端口
        ui.number(config.get_text("config_emulator_port"),
                step=1,
                precision=0,
                ).bind_value(config.userconfigdict, 'TARGET_PORT', forward=lambda v: int(v), backward=lambda v:int(v)).style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: not v)
        # 序列号
        ui.input(config.get_text("adb_serial")).bind_value(config.userconfigdict, 'ADB_SEIAL_NUMBER').style('width: 400px').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)
        
        # 切换使用序列号还是IP+端口
        ui.checkbox(config.get_text("adb_direct_use_serial")).bind_value(config.userconfigdict, 'ADB_DIRECT_USE_SERIAL_NUMBER')
        
    
    with ui.row():
        kill_port = ui.checkbox(config.get_text("config_kill_port")).bind_value(config.userconfigdict, "KILL_PORT_IF_EXIST")
        kill_port.set_value(False)
        kill_port.set_enabled(False)
    
    with ui.row():
        ui.checkbox(config.get_text("config_physics")).bind_value(config.userconfigdict, 'CONFIG_PHYSICS').bind_visibility_from(config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)
    
    with ui.row().bind_visibility_from(config.userconfigdict, "CONFIG_PHYSICS", lambda v: not v):    
        ui.input(config.get_text("config_emulator_path"),
                    ).bind_value(config.userconfigdict, 'TARGET_EMULATOR_PATH',forward=lambda v: v.replace("\\", "/").replace('"','')).style('width: 400px')
    
    # 结束后自动关闭操作
    with ui.card().bind_visibility_from(config.userconfigdict, "CONFIG_PHYSICS", lambda v: not v):
        with ui.row():
            ui.checkbox(config.get_text("config_close_emulator_when_finish")).bind_value(config.userconfigdict, 'CLOSE_EMULATOR_FINISH')
            ui.checkbox(config.get_text("config_close_even_if_error")).bind_value(config.userconfigdict, 'CLOSE_EMULATOR_ERROR').bind_visibility_from(config.userconfigdict, "CLOSE_EMULATOR_FINISH")
    with ui.card():
        with ui.row():
            ui.checkbox(config.get_text("config_close_game_when_finish")).bind_value(config.userconfigdict, 'CLOSE_GAME_FINISH')
            ui.checkbox(config.get_text("config_close_even_if_error")).bind_value(config.userconfigdict, 'CLOSE_GAME_ERROR').bind_visibility_from(config.userconfigdict, "CLOSE_GAME_FINISH")
    
    with ui.card():
        with ui.row():
            ui.checkbox(config.get_text("config_close_BAAH_when_finish")).bind_value(config.userconfigdict, 'CLOSE_BAAH_FINISH')
            ui.checkbox(config.get_text("config_close_even_if_error")).bind_value(config.userconfigdict, 'CLOSE_BAAH_ERROR').bind_visibility_from(config.userconfigdict, "CLOSE_BAAH_FINISH")

    # 登录超时重启模拟器
    ui.number(config.get_text("config_login_timeout"), min=180, precision=0, step=1).bind_value(config.userconfigdict, "GAME_LOGIN_TIMEOUT", forward= lambda x: int(x)).style("width: 200px")
    ui.number(config.get_text("config_max_emulator_restart_times"), min=0, max=10, precision=0, step=1).bind_value(config.userconfigdict, "MAX_RESTART_EMULATOR_TIMES", forward= lambda x: int(x)).style("width: 400px").bind_visibility_from(config.userconfigdict, "CONFIG_PHYSICS", lambda v: not v)