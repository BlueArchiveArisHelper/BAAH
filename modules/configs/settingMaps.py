# 用户的config里值之间的对应关系
# 对应关系应当写进defaultSettings.py里
import hashlib

server2pic = {
    "JP":"./DATA/assets_jp",
    "GLOBAL":"./DATA/assets",
    "GLOBAL_EN":"./DATA/assets_global_en",
    "CN":"./DATA/assets_cn",
    "CN_BILI":"./DATA/assets_cn",
    "PC_STEAM":"./DATA/assets",
    "PC_STEAM_EN":"./DATA/assets_global_en",
    "PC_JP":"./DATA/assets_jp"
}

server2activity = {
    "JP":"com.YostarJP.BlueArchive/com.yostarjp.bluearchive.MxUnityPlayerActivity",
    "GLOBAL_EN":"com.nexon.bluearchive/.MxUnityPlayerActivity",
    "GLOBAL":"com.nexon.bluearchive/.MxUnityPlayerActivity",
    "CN":"com.RoamingStar.BlueArchive/com.yostar.supersdk.activity.YoStarSplashActivity",
    "CN_BILI":"com.RoamingStar.BlueArchive.bilibili/com.yostar.supersdk.activity.YoStarSplashActivity",
    "PC_STEAM":"Blue Archive/BlueArchive.exe",  # 包名为窗口名/进程名
    "PC_STEAM_EN":"Blue Archive/BlueArchive.exe",  # 包名为窗口名/进程名
    "PC_JP":"ブルーアーカイブ/Blue Archive.exe",  # 包名为窗口名/进程名
}


# important
activity2server = {v:k for k,v in server2activity.items()}

server2respond = {
    "JP":40,
    "GLOBAL":40,
    "GLOBAL_EN":40,
    "CN":40,
    "CN_BILI":40,
    "PC_STEAM": 20,
    "PC_STEAM_EN": 20,
    "PC_JP": 10,
}

def configname2screenshotname(configfilename):
    """
    根据config文件名，返回截图文件名
    config文件名包含后缀不包含路径
    """
    screenshotfilehash = hashlib.sha1(configfilename.encode('utf-8')).hexdigest()
    # 如果长度大于8，截取前8位
    if len(screenshotfilehash) > 8:
        screenshotfilehash = screenshotfilehash[:8]
    # 如果长度小于8，补0
    elif len(screenshotfilehash) < 8:
        screenshotfilehash = screenshotfilehash.zfill(8)
    return screenshotfilehash + ".png"


def old_VPN2action_flow(VPN_json):
    """
    把老版本的VPN json变成flow的格式
    """
    # 由于这边是底层依赖，不能 import 任何项目组件，所有东西用json表示
    try:
        vpn_app = VPN_json["VPN_ACTIVITY"] if VPN_json["VPN_ACTIVITY"] else ""
        vpn_list = VPN_json["CLICK_AND_WAIT_LIST"] if VPN_json["CLICK_AND_WAIT_LIST"] else []
        g_action_open_app = lambda _id,_app: {
                    "id_n": "do_action_f",
                    "id": str(_id),
                    "i_f_o": [
                        {
                            "id_n": "open_apk_package_a",
                            "a_p": [
                                {
                                    "id_n": "package",
                                    "p_v": _app
                                }
                            ]
                        }
                    ]
                }
        g_action_click_pic=lambda _id, _pic:{
                    "id_n": "run_until_f",
                    "id": str(_id),
                    "i_f_o": [
                        {
                            "id_n": "maxtimes",
                            "p_v": 3.0
                        },
                        {
                            "id_n": "click_pic_a",
                            "a_p": [
                                {
                                    "id_n": "picPath",
                                    "p_v": _pic
                                },
                                {
                                    "id_n": "threshold",
                                    "p_v": 0.9
                                }
                            ]
                        },
                        {
                            "id_n": "img_not_match_p",
                            "c_obj": None,
                            "c_v": [
                                {
                                    "id_n": "picPath",
                                    "p_v": _pic
                                },
                                {
                                    "id_n": "threshold",
                                    "p_v": 0.9
                                }
                            ]
                        }
                    ]
                }
        g_action_click_xy = lambda _id, x, y:{
                    "id_n": "do_action_f",
                    "id": str(_id),
                    "i_f_o": [
                        {
                            "id_n": "click_xy_a",
                            "a_p": [
                                {
                                    "id_n": "x",
                                    "p_v": int(x)
                                },
                                {
                                    "id_n": "y",
                                    "p_v": int(y)
                                }
                            ]
                        }
                    ]
                }
        g_action_sleep = lambda _id, ti_s:{
                    "id_n": "do_action_f",
                    "id": str(_id),
                    "i_f_o": [
                        {
                            "id_n": "sleep_time_a",
                            "a_p": [
                                {
                                    "id_n": "time_seconds",
                                    "p_v": ti_s
                                }
                            ]
                        }
                    ]
                }
        
        _id = 10000
        res_list = [g_action_open_app(_id, vpn_app), g_action_sleep(_id+1, 5)] if vpn_app else []
        _id += 2
        for each in vpn_list:
            if isinstance(each[0], str):
                res_list.append(g_action_click_pic(_id, each[0]))
            else:
                res_list.append(g_action_click_xy(_id, each[0][0], each[0][1]))
            _id += 1
            res_list.append(g_action_sleep(_id, each[1]))
            _id += 1
        return {"a_l":res_list}
    except:
        print("Error when parse old VPN setting into obj workflows")
        return {}
