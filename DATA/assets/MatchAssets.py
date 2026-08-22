
class MatchAssets:
    """
    记录关键点位置或者颜色
    """

    CENTER = (1280//2, 720//2)
    """
    Center of the screen
    """
    MAGICPOINT = (300, 2)
    """
    Magicpoint is the point that never contains any activable item
    """
    HOMEPOINT = (1236, 25)
    """
    Most of the time, the home icon on the top right corner
    """
    TOPLEFTBACK = (56, 28)
    """
    The circle back icon on the top left corner
    """

    COLOR_WHITE = ((230, 230, 230), (255, 255, 255))
    COLOR_RED = ((24, 70, 250), (26, 72, 252))
    COLOR_BUTTON_WHITE = ((220, 220, 220), (255, 255, 255))
    """
    用于交战时右上角暂停按钮的像素识别，按钮有时半透明，受到游戏内交战环境影响，阈值可以低点
    """

    COLOR_BUTTON_GRAY = ((200, 200, 200), (230, 230, 230))

    COLOR_BUTTON_BLUE = ((250, 220, 135), (255, 232, 145))
    """列表关卡右侧蓝色可点击按钮"""
    COLOR_BUTTON_YELLOW = ((64, 222, 235), (84, 242, 255))
    """黄色按钮"""
    
    COLOR_PINK = ((175, 130, 250 ), (202, 155, 255 ))
    """
    用于判断是否在活动中，如果在活动（双倍/三倍活动）中，这个颜色的横幅会出现在选关时左上角
    """
    
    LEFT_FOUR_TEAMS_POSITIONS = (
        [128, 186],
        [124, 266],
        [123, 344],
        [122, 424]
    )
    """队伍选择界面，左侧四个队伍的选择按钮坐标"""
    COLOR_SELECTED_LEFT_FOUR_TEAM = ((90, 60, 35), (110, 80, 55))
    """队伍选择界面，左侧四个队伍的选择按钮被选择后的颜色"""

    COLOR_HOME_LEFT_NICKNAME = ((110, 60, 5), (130, 80, 45))
    """主页左上角昵称的颜色范围"""