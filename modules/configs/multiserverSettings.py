# ! 除了assets，此文件禁止引入任何其他baah自身项目模块，避免循环引用
from DATA.assets.PageName import PageName
from DATA.assets.PopupName import PopupName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.MatchAssets import MatchAssets
#
import traceback
# 集中管理多服务器中的同个素材的不同坐标/像素值
# 通过 serverAssetMapping 字典规定不同服务器所使用的某个素材的坐标/像素值

# 以下几个在外部使用 is_server_type_in_group, MultiServerType, get_correct_asset, AssetMappingKeys

class ServerTypes:
    # 最基础的配置文件里的服务器类型枚举
    JP = "JP"
    GLOBAL = "GLOBAL"
    GLOBAL_EN = "GLOBAL_EN"
    CN = "CN"
    CN_BILI = "CN_BILI"
    PC_STEAM = "PC_STEAM"
    PC_STEAM_EN = "PC_STEAM_EN"
    PC_EXE_JP = "PC_EXE_JP"

# 打印ServerTypes的所有属性
__all_server_types = [attr for attr in dir(ServerTypes) if not attr.startswith("__") and not callable(getattr(ServerTypes, attr))]

class MultiServerType:
    """
    不同服务器分类，注意并非为单一SERVER_TYPE名字，这里的某个字段可能包含多个SERVER_TYPE含义，例如 Japan 包含 JP 和 PC_EXE_JP 两种。
    """
    # -----------按服务器分的集合名（8）-----------
    
    JapanGroup = (ServerTypes.JP, ServerTypes.PC_EXE_JP)
    """所有日服"""

    GlobalGroup = (ServerTypes.GLOBAL, ServerTypes.GLOBAL_EN , ServerTypes.PC_STEAM, ServerTypes.PC_STEAM_EN)
    """所有国际服"""

    CNGroup = (ServerTypes.CN, ServerTypes.CN_BILI)
    """所有国服"""

    # -----------按平台分的集合名（8）-----------
    AndroidGroup = (ServerTypes.JP, ServerTypes.GLOBAL, ServerTypes.GLOBAL_EN, ServerTypes.CN, ServerTypes.CN_BILI)
    """所有安卓应用"""
    
    PCGroup = (ServerTypes.PC_EXE_JP, ServerTypes.PC_STEAM, ServerTypes.PC_STEAM_EN)
    """所有PC上跑的"""

    # ----------细分PC平台的Steam和独立EXE应用-----------
    GlobalAndroidGroup = (ServerTypes.GLOBAL, ServerTypes.GLOBAL_EN)
    """所有安卓上的国际服"""

    SteamGroup = (ServerTypes.PC_STEAM, ServerTypes.PC_STEAM_EN)
    """所有Steam应用"""

    PCEXEGroup = (ServerTypes.PC_EXE_JP)
    """所有PC独立EXE应用"""

    # -----------单个独立的服务器类型（8）-----------
    JPSingle = (ServerTypes.JP,)
    GlobalSingle = (ServerTypes.GLOBAL,)
    GlobalENSingle = (ServerTypes.GLOBAL_EN,)
    CNSingle = (ServerTypes.CN,)
    CNBiliSingle = (ServerTypes.CN_BILI,)
    PC_STEAMSingle = (ServerTypes.PC_STEAM,)
    PC_STEAM_ENSingle = (ServerTypes.PC_STEAM_EN,)
    PC_EXE_JPSingle = (ServerTypes.PC_EXE_JP,)

    # -----------虚拟剩余服务器，主要用于serverAssetMapping里表示除了指定服务器之外的所有服务器-----------
    Other_groups = "Other_groups"


def is_server_type_in_group(config, group) -> bool:
    """
    判断某个服务器类型是否在某个服务器组中

    Param:
    config
        可以是配置文件对象，也可以是 SERVER_TYPE 配置项目
    group
        可以是单个ServerTypes属性，也可以是MultiServerType属性
    """
    try:
        if isinstance(config, str): # 兼容字符串
            server_type = config
        else:
            server_type = config.userconfigdict["SERVER_TYPE"]
        if isinstance(group, str): # 兼容单个字符串的情况
            group = [group]
        return server_type in group
    except Exception as e:
        print(f"Warning: SERVER_TYPE not found in config.userconfigdict, cannot determine server type. {traceback.format_exc()}")
    return False

# -----------------多服务器素材映射表-----------------

class AssetMappingKeys:
    """素材在不同服务器的映射"""
    # 登录后的社区弹窗的关闭位置
    CLOSE_LOGIN_SHEQU_POPUP = {
        MultiServerType.SteamGroup: (1123, 114),
        MultiServerType.Other_groups: (1226, 56)
    }
    # 主页判断是否有弹窗的像素点位置
    CHECK_HOMEPAGE_HAS_POPUP_POS = {
        MultiServerType.CNGroup: (1027, 49),
        MultiServerType.Other_groups: (8, 26)
    }
    # 主页判断是否有弹窗的像素点颜色
    CHECK_HOMEPAGE_HAS_POPUP_COLOR = {
        MultiServerType.CNGroup: MatchAssets.COLOR_WHITE,
        MultiServerType.Other_groups: MatchAssets.COLOR_HOME_LEFT_NICKNAME
    }
    # 主页识别资源 power
    HOME_OCR_POWER_REGION = {
        MultiServerType.CNGroup: ((483, 17), (582, 56)),
        MultiServerType.Other_groups: ((537, 24), (612, 49))
    }
    # 主页识别资源 credit
    HOME_OCR_CREDIT_REGION = {
        MultiServerType.CNGroup: ((668, 19), (812, 59)),
        MultiServerType.Other_groups: ((699, 24), (844, 47))
    }
    # 主页识别资源 diamond
    HOME_OCR_DIAMOND_REGION = {
        MultiServerType.CNGroup: ((863, 21), (973, 60)),
        MultiServerType.Other_groups: ((899, 24), (1002, 48))
    }
    # 主页右下角进入一堆活动页面的按钮位置
    HOME_FIGHT_CENTER_POS = {
        MultiServerType.CNGroup: (1196, 567),
        MultiServerType.Other_groups: (1196, 650)
    }
    # FIGHT_CENTER进入悬赏通缉的点击坐标
    FIGHT_CENTER_WANTED_POS = {
        MultiServerType.CNGroup: (741, 440),
        MultiServerType.Other_groups: (746, 367)
    }
    # FIGHT_CENTER进入特殊任务的点击坐标
    FIGHT_CENTER_SPECIAL_POS = {
        MultiServerType.CNGroup: (721, 538),
        MultiServerType.Other_groups: (728, 481)
    }
    # FIGHT_CENTER进入活动一栏的点击坐标
    EVENT_RECAP_ENTRY_POS = {
        MultiServerType.CNGroup: (1049, 558),
        MultiServerType.Other_groups: (1055, 620)
    }
    # FIGHT_CENTER左侧进入当期活动的点击坐标，刚好能点进活动但是又点不到活动页面左上角圆形icon
    EVENT_ENTRY_POS = {
        MultiServerType.CNGroup: (35, 110),
        MultiServerType.Other_groups: (52, 137)
    }
    # 活动一栏x轴y轴黄点linspace分布
    EVENT_RECAP_YELLOW_GRID = {
        MultiServerType.JapanGroup: ((783, 1215, 3), (156, 495, 3)),
        MultiServerType.CNGroup: ((786, 1228, 3), (155, 502, 3)),
        MultiServerType.Other_groups: ((790, 1222, 3), (155, 494, 3))
    }
    # 每日免费奖励弹窗里的tab页签红点位置以及要点击页签的位置
    FREE_AWARD_TAB_POSITIONS = {
        MultiServerType.JapanGroup: ((228, 222), (66, 233)),
        MultiServerType.Other_groups: ((1030, 153), (900, 181))
    }
    # 主页进入商店的点击位置
    SHOP_ENTRY_POS = {
        MultiServerType.JapanGroup: (775, 677),
        MultiServerType.Other_groups: (795, 667)
    }
    # 格子推图 跳过战斗和自动结束打勾的位置
    GRID_AUTO_SETTINGS_POSITIONS = {
        MultiServerType.CNGroup: ((1121, 551), (1080, 606)),
        MultiServerType.JapanGroup: ((1088, 550), (952, 604)),
        (ServerTypes.GLOBAL, ServerTypes.PC_STEAM): ((1116, 550), (1055, 605)),
        (ServerTypes.GLOBAL_EN,ServerTypes.PC_STEAM_EN): ((1096, 550), (1045, 604))
    }
    # 格子推图 识别当前队伍编号的位置
    GRID_TEAM_NUMBER_OCR_REGION = {
        (ServerTypes.GLOBAL, ServerTypes.PC_STEAM): ((72, 544), (91, 569)),
        MultiServerType.Other_groups: ((117, 544), (136, 569))
    }
    # 格子推图 人物头顶黄色蒙版颜色范围
    # 国服的走格子头顶黄色箭头颜色暗一点,有些关卡敌人会有黄色感叹号(16, 219, 255)
    # 有些关卡敌人会有黄色感叹号，那个的第一位在30或40左右，第二位在220左右。hard关头顶有灯照着时，第一个数字会变暗。
    GRID_HEAD_YELLOW_COLOR = {
        MultiServerType.CNGroup: ((2, 222, 249), (33, 233, 255)),
        MultiServerType.Other_groups: ((4, 223, 254), (33, 235, 255))
    }
    # 登录时检查活动弹窗，左下角今日不再显示的勾勾的ocr区域
    LOGIN_EVENT_CHECK_REGION = {
        MultiServerType.SteamGroup: ((260, 513), (294, 545)),
        MultiServerType.Other_groups: ((30, 662), (63, 691))
    }
    # 登录时检查活动弹窗，左下角今日不再显示中心坐标
    LOGIN_EVENT_CHECKBOX_POS = {
        MultiServerType.SteamGroup: (269, 534),
        MultiServerType.Other_groups: (65, 676)
    }
    # 登陆时活动弹窗右上角关闭位置
    LOGIN_EVENT_CLOSE_POS = {
        MultiServerType.SteamGroup: (1023, 123),
        MultiServerType.Other_groups: None
    }


def get_correct_asset(config, asset_mapping):
    """
    根据当前服务器类型，查找对应的素材坐标/像素值

    Params:
        config: 用户使用的config
        asset_mapping: AssetMappingKeys下的静态变量
    """
    server_type = config.userconfigdict["SERVER_TYPE"]

    # 先检查是否有匹配的服务器组
    for group, value in asset_mapping.items():
        if group != MultiServerType.Other_groups and server_type in group:
            return value

    # 如果没有匹配的服务器组，则检查是否有Other_groups
    if MultiServerType.Other_groups in asset_mapping:
        return asset_mapping[MultiServerType.Other_groups]

    raise ValueError(f"No matching asset found for server type '{server_type}'.")


# 引入本文件时自动检查是否 每个 服务器类型都在serverAssetMapping中有对应的素材索引或者该素材索引中有Other_groups
def check_whether_serverAssetMapping_correct():
    for assetkey, mappings in vars(AssetMappingKeys).items():
        if assetkey.startswith("__") or not isinstance(mappings, dict):
            continue
        # print("Checking ", assetkey)
        # 有Other_groups的话不用检查了
        if MultiServerType.Other_groups in mappings:
            continue
        # 否则检查对于每种服务器类型，是否能够找到对应素材值
        for each_real_servertype in __all_server_types:
            has_corresponding_key = False
            for group_key in mappings:
                if each_real_servertype in group_key:
                    has_corresponding_key = True
                    break
            if has_corresponding_key is False:
                raise Exception(f"Can not find asset value! target server: ({each_real_servertype}), target asset: ({assetkey})")
    return True

check_whether_serverAssetMapping_correct()
