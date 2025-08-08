# 用户的config里值之间的对应关系
# 对应关系应当写进defaultSettings.py里
import hashlib

server2pic = {
    "JP":"./DATA/assets_jp",
    "GLOBAL":"./DATA/assets",
    "GLOBAL_EN":"./DATA/assets_global_en",
    "CN":"./DATA/assets_cn",
    "CN_BILI":"./DATA/assets_cn"
}

server2activity = {
    "JP":"com.YostarJP.BlueArchive/com.yostarjp.bluearchive.MxUnityPlayerActivity",
    "GLOBAL_EN":"com.nexon.bluearchive/.MxUnityPlayerActivity",
    "GLOBAL":"com.nexon.bluearchive/.MxUnityPlayerActivity",
    "CN":"com.RoamingStar.BlueArchive/com.yostar.supersdk.activity.YoStarSplashActivity",
    "CN_BILI":"com.RoamingStar.BlueArchive.bilibili/com.yostar.supersdk.activity.YoStarSplashActivity"
}


# important
activity2server = {v:k for k,v in server2activity.items()}

server2respond = {
    "JP":40,
    "GLOBAL":40,
    "GLOBAL_EN":40,
    "CN":40,
    "CN_BILI":40
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