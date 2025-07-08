from modules.configs.settingMaps import *

from time import time

# 用户的脚本config里的默认值以及可选值
# 如果用户的config里没有某个值，先看能否用settingMaps里映射出来，如果不能，就用默认值代替
# 注意解析链：(default/map/read) -> post parse


# d: default value 默认值
# s: selective value 可选值
# m: map value 映射方法
    # from: map value的来源key
    # map: map value的映射函数，默认是 lambda x=parsedjson[from]: ...
# p: post parse action 后解析方法，默认是lambda value, parsedjson: ...，如果需要在解析后对值执行一些固定的判断和替换，可以在这重写

# selective value作为提醒值存在，主要的map映射应当在settingMaps里，-》myAllTask.parse_task

# userconfigdict是一个dict，存储用户的一个脚本的BAAH配置文件的内容，用户可以在GUI里修改这些值
defaultUserDict = {
    "TIMETABLE_TASK": {"d":[]},
    "WANTED_HIGHEST_LEVEL": {"d":[]},
    "SPECIAL_HIGHTEST_LEVEL": {"d":[]},
    "EXCHANGE_HIGHEST_LEVEL": {"d":[]},
    "EVENT_QUEST_LEVEL": {"d":[]},
    "HARD": {"d":[]},
    "NORMAL": {"d":[]},
    "TASK_ORDER": {"d": []},
    "SHOP_NORMAL": {"d":[]},
    "SHOP_NORMAL_BUYALL": {"d":False},
    "SHOP_CONTEST": {"d":[]},
    "SHOP_CONTEST_BUYALL": {"d":False},
    "PUSH_NORMAL_USE_SIMPLE": {"d":False},
    "PUSH_NORMAL_QUEST": {"d":0},
    "PUSH_NORMAL_QUEST_LEVEL": {"d":1},
    "PUSH_HARD_USE_SIMPLE": {"d":False},
    "PUSH_HARD_QUEST": {"d":0},
    "PUSH_HARD_QUEST_LEVEL": {"d":1},
    "TASK_ACTIVATE": {"d":[]},
    # new config in 1.2.x
    "SERVER_TYPE":{
        "d":"GLOBAL",
        "s":["GLOBAL", "GLOBAL_EN", "JP", "CN", "CN_BILI"],
        "m": {
            "from": "ACTIVITY_PATH",
            "map": lambda x: activity2server[x] if x in activity2server else "GLOBAL"
        }
    },
    "UPDATE_API_URL": {
        "d":"https://baah.02000721.xyz/apk/global",
        "m": {
            "from": "SERVER_TYPE",
            "map": lambda x: server2url[x] if x in server2url else "https://baah.02000721.xyz/apk/global"
        }
    },
    "TARGET_EMULATOR_PATH":{"d":""},
    "CLOSE_EMULATOR_BAAH":{"d":False}, # deprecate
    "CLOSE_EMULATOR_FINISH":{
        "d": False,
        "m": {
            "from": "CLOSE_EMULATOR_BAAH",
            "map": lambda x: x
        }
    },
    "CLOSE_GAME_FINISH":{
        "d": False,
        "m": {
            "from": "CLOSE_EMULATOR_BAAH",
            "map": lambda x: x
        }
    },
    "CLOSE_BAAH_FINISH":{
        "d": False,
        "m": {
            "from": "CLOSE_EMULATOR_BAAH",
            "map": lambda x: x
        }
    },
    # 发生异常报错后是否关闭模拟器
    "CLOSE_EMULATOR_ERROR":{
        "d": False,
    },
    "CLOSE_GAME_ERROR":{
        "d": False,
    },
    "CLOSE_BAAH_ERROR":{
        "d": False,
    },
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
    # "FANHEXIE":{"d":False}, # 于1.7.5弃用反和谐设置，对于反和谐差异图片进行动态匹配
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
        },
        "p": lambda val, parsedjson: server2respond[parsedjson["SERVER_TYPE"]] if parsedjson["LOCK_SERVER_TO_RESPOND_Y"] and parsedjson["SERVER_TYPE"] in server2respond else val # 如果开启了跟随服务器版本，则一直使用服务器版本映射出的y响应坐标
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
    "CAFE_TOUCH_WAY_DIFF":{"d":True},
    "USE_VPN":{"d":False},
    "VPN_CONFIG":{"d":{
        "VPN_ACTIVITY":"com.github.kr328.clash/com.github.kr328.clash.MainActivity",
        "CLICK_AND_WAIT_LIST":[[[622, 248], 2]],
    }},
    "CLOSE_VPN":{"d":False},
    "VPN_CLOSE_CONFIG":{"d":{
        "VPN_ACTIVITY":"com.github.kr328.clash/com.github.kr328.clash.MainActivity",
        "CLICK_AND_WAIT_LIST":[[[622, 248], 2]],
    }},
    "AUTO_PUSH_EVENT_QUEST":{"d":True},
    "CAFE_COLLECT":{"d":True},
    "CAFE_TOUCH":{"d":True},
    "CAFE_INVITE":{
        "d":True,
        "p": lambda val, parsedjson: True # 1.8.10 deprecated
    },
    "RAISE_ERROR_IF_CANNOT_PUSH_EVENT_QUEST":{"d":True},
    
    # 多倍活动开启状态相关
    "SPEICAL_EVENT_STATUS":{"d":False},
    "NORMAL_QUEST_EVENT_STATUS":{"d":False},
    "HARD_QUEST_EVENT_STATUS":{"d":False},
    "EXCHANGE_EVENT_STATUS":{"d":False},



    # 邮件相关
    "MAIL_USER":{"d":""},
    "MAIL_PASS":{"d":""},
    "ADVANCED_EMAIL":{"d":False},
    "SENDER_EMAIL":{"d":""},
    "RECEIVER_EMAIL":{"d":""},
    "MAIL_HOST":{"d":""},
    
    "AUTO_ASSAULT_LEVEL":{"d":4},
    
    "RUN_UNTIL_TRY_TIMES":{"d":9},
    "RUN_UNTIL_WAIT_TIME":{"d":0.6},
    
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
    "SMART_TIMETABLE":{"d":True},
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
    
    # 自定义任务
    "USER_DEF_TASKS":{"d":""},
    
    "CRAFT_TIMES":{"d":1},
    
    # 竞技场优先级、
    "CONTEST_LEVEL_PRIORITY":{"d":10},
    "CONTEST_RANK_PRIORITY":{"d":10},

    # 游戏启动超时时间，秒。防止意料之外的错误判断（超时会触发error），默认超时时间设长点
    "GAME_LOGIN_TIMEOUT":{"d":600},
    # 游戏卡启动时的重新启动模拟器最多尝试次数
    "MAX_RESTART_EMULATOR_TIMES":{"d":0},

    # 截图模式, png：保存/读取png图片，pipe读取/单例化管道内数据
    "SCREENSHOT_METHOD":{
        "d":"pipe",
        "s":["png", "pipe"]
    },

    # 是否执行游戏登录任务（与游戏打开登录，统计消耗的体力，金币，钻石有关）
    "OPEN_GAME_APP_TASK":{
        "d":True
    },
    # 是否执行所有任务结束后的尾部任务（与统计消耗的体力，金币，钻石有关）
    "DO_POST_ALL_TASK":{
        "d":True
    },
    # 用户设置的现有配队的属性强度
    # y一维列表，第一维表示队伍，元素是一个dict表示队伍的属性对应强度(0-10)，属性先认为是4种，{red, blue, yellow, purple}
    "TEAM_SET_STRENGTH":{
        "d": [
            {"red":10, "blue":10, "yellow":10, "purple":10},
            {"red":10, "blue":10, "yellow":10, "purple":10},
            {"red":10, "blue":10, "yellow":10, "purple":10},
            {"red":0, "blue":0, "yellow":0, "purple":0}
        ]
    },

    # 咖啡馆设置
    # 要邀请的学生在momotalk中的序号，从1开始
    "CAFE1_INVITE_SEQ":{"d":1},
    "CAFE2_INVITE_SEQ":{"d":2},
    # 咖啡馆邀请发生同名时是否向后顺延邀请序号
    "CAFE_INVITE_SAME_NAME_DELAY":{"d":False},
    # 咖啡馆邀请顺延时是否逆向（向前一位顺延）
    "CAFE_INVITE_SAME_NAME_DELAY_REVERSE":{"d":False},
    # 制造是否选择快速制造
    "CRAFT_USE_QUICK":{"d":False},
    # 一键扫荡
    "ONE_CLICK_RAID":{"d":[]},

    # 自动配队
    "IS_AUTO_ASSAULT_AUTO_TEAM":{"d":False},
    "ACTIVITY_AUTO_TEAM":{"d":False},
    "EXPLORE_AUTO_TEAM":{"d":False},
    # 一键扫讨是否只在有三倍活动下进行
    "DO_ONE_CLICK_RAID_ONLY_DURING_EVENT":{"d":False},
    "DO_ONE_CLICK_RAID_ONLY_DURING_NORMAL_TRIPLE":{"d":False},
    "DO_ONE_CLICK_RAID_ONLY_DURING_HARD_TRIPLE":{"d":False},

    # 用户存储文件的名字
    "USER_STORAGE_FILE_NAME":{
        "d":"userStorage",
        "m":{
            "from": "SCREENSHOT_NAME",
            "map": lambda x: x.replace(".png", ".json")
        }
    },
    # 综合战术考试 关卡
    "EXAM_TARGET_LEVEL":{
        "d":2
    },
    # 综合战术考试 考试队伍次数
    "EXAM_TEAM_COUNT":{
        "d":3
    },
    # ARIA2配置
    "ARIA2_PATH":{"d":"./tools/aria2/aria2c.exe"},
    "ARIA2_THREADS":{"d":16},
    "ARIA2_MAX_TRIES":{"d":5},
    "ARIA2_FAILURED_WAIT_TIME":{"d":0.5},
    
    # 大更新配置
    "BIG_UPDATE":{"d":False},
    "BIG_UPDATE_TYPE":{"d":"API",
                                        "s":["API", "URLGET"]},
    "CONFIG_PHYSICS":{"d":False}
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
        }},
    # 用户在GUI里的各种备注
    "NOTE":{"d":{
        "HARD_NOTE":"",
    }},
    # 是否输出日志
    "SAVE_LOG_TO_FILE":{"d":False},
    # 发生错误时，是否输出custom日志
    "SAVE_ERR_CUSTOM_LOG":{"d":True},
    # Mirror酱的密钥
    "SEC_KEY_M":{
        "d": "",
    },
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
    # 截图文件读取失败的次数
    "SCREENSHOT_READ_FAIL_TIMES":{"d":0},
    # 当前尝试重启模拟器次数
    "RESTART_EMULATOR_TIMES":{"d":0},
    # 截图数据，当SCREENSHOT_METHOD为pipe时使用
    "SCREENSHOT_DATA":{"d":None},
    # 记录这次运行执行到第几个任务了，任务开始时更新此项。-1表示之前没有执行任何任务
    "CURRENT_PERIOD_TASK_INDEX":{"d":-1},
}

# storagedict存储与某一个配置文件对应的游戏实例的持久性存储信息（如钻石历史变化曲线），其生命周期与userconfig相同，但是在脚本运行时是随用随写的
defaultStorageDict = {
    # 记录上一次存储 信用点和钻石的日期
    "LAST_SAVE_MONEY_DIAMOND_DATE":{"d":""},
    # 记录历史存储的 信用点和钻石和对应日期 列表
    "HISTORY_MONEY_DIAMOND_LIST":{"d":[]},
}