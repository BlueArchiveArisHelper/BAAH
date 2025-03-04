from modules.configs.settingMaps import *
from time import time

# 用户的脚本config里的默认值以及可选值
# 如果用户的config里没有某个值，先看能否用settingMaps里映射出来，如果不能，就用默认值代替
# 注意引用链

# d: default value 默认值
# s: selective value 可选值
# m: map value 映射方法
# from: map value的来源key
# map: map value的映射函数

# selective value作为提醒值存在，主要的map映射值应当在settingMaps里

defaultUserDict = {
    "TIMETABLE_TASK": {"d":[]},
    "WANTED_HIGHEST_LEVEL": {"d":[]},
    "SPECIAL_HIGHTEST_LEVEL": {"d":[]},
    "EXCHANGE_HIGHEST_LEVEL": {"d":[]},
    "EVENT_QUEST_LEVEL": {"d":[]},
    "HARD": {"d":[]},
    "NORMAL": {"d":[]},
    "TASK_ORDER": {"d":["登录游戏"]},
    "SHOP_NORMAL": {"d":[]},
    "SHOP_CONTEST": {"d":[]},
    "PUSH_NORMAL_QUEST": {"d":0},
    "PUSH_NORMAL_QUEST_LEVEL": {"d":1},
    "PUSH_HARD_QUEST": {"d":0},
    "PUSH_HARD_QUEST_LEVEL": {"d":1},
    "TASK_ACTIVATE": {"d":[True]},
    # new config in 1.2.x
    "SERVER_TYPE":{
        "d":"GLOBAL",
        "s":["GLOBAL", "GLOBAL_EN", "JP", "CN", "CN_BILI"],
        "m": {
            "from": "ACTIVITY_PATH",
            "map": lambda x: activity2server[x] if x in activity2server else "GLOBAL"
        }
    },
    "TARGET_EMULATOR_PATH":{"d":""},
    "CLOSE_EMULATOR_BAAH":{"d":False},
    "PIC_PATH":{
        "d":"./DATA/assets",
        "s":[
            "./DATA/assets",
            "./DATA/assets_cn",
            "./DATA/assets_jp",
            "./DATA/assets_global_en"
        ],
        "m":{
            "from" : "SERVER_TYPE",
             "map" : lambda x: server2pic[x] if x in server2pic else "./DATA/assets"
        }
    },
    "GRID_SOL_PATH":{
      "d":"./DATA/grid_solution"  
    },
    "FANHEXIE":{"d":False},
    "ACTIVITY_PATH":{
        "d":"com.nexon.bluearchive/.MxUnityPlayerActivity",
        "s":[
            "com.YostarJP.BlueArchive/com.yostarjp.bluearchive.MxUnityPlayerActivity",
            "com.nexon.bluearchive/.MxUnityPlayerActivity",
            "com.RoamingStar.BlueArchive/com.yostar.supersdk.activity.YoStarSplashActivity",
            "com.RoamingStar.BlueArchive.bilibili/com.yostar.supersdk.activity.YoStarSplashActivity"
        ],
        "m":{
            "from": "SERVER_TYPE",
            "map": lambda x: server2activity[x] if x in server2activity else "com.nexon.bluearchive/.MxUnityPlayerActivity",
        }
    },
    "NEXT_CONFIG" : {"d":""},
    "ADB_PATH":{"d":"./tools/adb/adb.exe"},
    "SCREENSHOT_NAME":{
        "d":"screenshot.png"
    },
    "TARGET_IP_PATH":{"d":"127.0.0.1"},
    "TARGET_PORT":{"d":5555},
    "KILL_PORT_IF_EXIST":{"d":False},
    "TIME_AFTER_CLICK":{"d": 0.7},
    "RESPOND_Y":{
        "d": 40,
        "m":{
            "from": "SERVER_TYPE",
            "map": lambda x: server2respond[x] if x in server2respond else 40
        }
    },
    "SHOP_NORMAL_REFRESH_TIME":{"d": 0},
    'SHOP_NORMAL_SWITCH':{"d":True},
    "SHOP_CONTEST_REFRESH_TIME":{"d": 0},
    'SHOP_CONTEST_SWITCH':{"d":True},

    "LOCK_SERVER_TO_RESPOND_Y":{"d": True},
    "CAFE_CAMERA_FULL":{"d":True},
    "AUTO_EVENT_STORY_PUSH":{"d":False},
    "EXPLORE_RAINBOW_TEAMS":{"d":False},
    "ENABLE_MAIL_NOTI":{"d":False},
    "CAFE_TOUCH_WAY_DIFF":{"d":False},
    "USE_VPN":{"d":False},
    "VPN_CONFIG":{"d":{
        "VPN_ACTIVITY":"com.github.kr328.clash/com.github.kr328.clash.MainActivity",
        "CLICK_AND_WAIT_LIST":[[[622, 248], 2]],
    }},
    "AUTO_PUSH_EVENT_QUEST":{"d":True},
    "CAFE_COLLECT":{"d":True},
    "CAFE_TOUCH":{"d":True},
    "CAFE_INVITE":{"d":True},
    "CAFE_INVITE1":{"d":True},
    "CAFE_INVITE2":{"d":True},
    "RAISE_ERROR_IF_CANNOT_PUSH_EVENT_QUEST":{"d":True},
    
    # 邮件相关
    "MAIL_USER":{"d":""},
    "MAIL_PASS":{"d":""},
    "ADVANCED_EMAIL":{"d":False},
    "SENDER_EMAIL":{"d":""},
    "RECEIVER_EMAIL":{"d":""},
    "MAIL_HOST":{"d":""},
    
    "AUTO_ASSAULT_LEVEL":{"d":4},
    
    "RUN_UNTIL_TRY_TIMES":{"d":6},
    "RUN_UNTIL_WAIT_TIME":{"d":1.5},
    
    # 是否直接使用emulator-5554这种序列号
    "ADB_DIRECT_USE_SERIAL_NUMBER":{"d":False},
    "ADB_SEIAL_NUMBER":{"d":"emulator-5554"},
    # 是否助战学生
    "IS_AUTO_ASSAULT_STUDENT_HELP":{"d":False},
    "AUTO_ASSAULT_HELP_STUDENT_IS_SUPPORT":{"d":False},
    "AUTO_ASSAULT_HELP_STUDENT":{"d":""},
    # 是否Http通知
    "ENABLE_HTTP_NOTI":{"d":False},
    "TARGET_HTTP_URL":{"d":""},
    "TARGET_HTTP_TOKEN":{"d":""},
    
    # 是否直接在内存中获取图像数据
    "USE_MEMORY_IMAGE":{"d":False},
    
    # 时间表是否自动选择
    "SMART_TIMETABLE":{"d":False},
    # 时间表各项权重
    "TIMETABLE_WEIGHT_OF_REWARD":{"d":10},
    "TIMETABLE_WEIGHT_OF_HEART":{"d":20},
    "TIMETABLE_WEIGHT_OF_LOCK":{"d":10},
    
    # 购买体力的最高单价价格，包含
    "BUY_AP_MAX_PRICE":{"d":30},
    "BUY_AP_ADD_TIMES":{"d":1},
    
    # 任务运行前后的命令
    "PRE_COMMAND":{"d":""},
    "POST_COMMAND":{"d":""},
}

# 软件的config里的默认值

defaultSoftwareDict = {
    "LANGUAGE":{"d":"zh_CN", "s":["zh_CN", "en_US"]},
    # "MAIL_USER":{"d":""},  # 弃用
    # "MAIL_PASS":{"d":""},  # 弃用
    # "ADVANCED_EMAIL":{"d":False},  # 弃用
    # "SENDER_EMAIL":{"d":""},  # 弃用
    # "RECEIVER_EMAIL":{"d":""},  # 弃用
    # "MAIL_HOST":{"d":""},  # 弃用
    "ENCRYPT_KEY":{
        "d":"54321",
        "m":{
            "from": "LANGUAGE", # map功能必须要有from字段，这里充当占位符
            # 使用现在的时间戳作为加密key，长度截取最后五位，字符串！
            "map": lambda x:  str(int(time()))[-5:]
        }}
}

# sessiondict是一个dict，存储一个BAAH配置任务的运行时信息，每次运行的时候都会按照以下内容初始化一个新的sessiondict
defaultSessionDict = {
    "PORT_IS_USED":{"d":False},
    "EMULATOR_PROCESS_PID":{"d":None},
    "GUI_OPEN_IN_WEB":{"d":True},
    "LAST_TEAM_SET":{"d":[]},
    "CAFE_HAD_INVITED":{"d":True},
    "TIMETABLE_NO_TICKET":{"d":False},
    "BAAH_START_TIME":{"d":""},
    "BEFORE_BAAH_SOURCES":{"d":{"power":0, "credit":0, "diamond":0}},
    "AFTER_BAAH_SOURCES":{"d":{"power":0, "credit":0, "diamond":0}},
    "CONTEST_NO_TICKET":{"d":False},
    "HAS_ENTER_EVENT":{"d":False},
    "INFO_DICT":{"d":{}},
    "INFO_LIST":{"d":[]},
    # 截图文件读取失败的次数
    "SCREENSHOT_READ_FAIL_TIMES":{"d":0},
}