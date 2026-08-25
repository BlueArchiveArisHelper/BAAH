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
    """
    try:
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


def get_correct_asset(config, asset_mapping):
    """
    根据当前服务器类型，查找对应的素材坐标/像素值

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
