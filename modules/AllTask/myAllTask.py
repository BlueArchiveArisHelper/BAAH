from enum import Enum
from modules.AllTask import *

from modules.AllPage.Page import Page

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, screenshot
from modules.utils.log_utils import logging, istr, CN, EN
from modules.configs.MyConfig import config

class TaskName():
    """
    配置文件里的task任务名称，此类下的属性可作为task标识符
    """
    LOGIN_GAME = "登录游戏"
    MOMOTALK = "清momotalk"
    CAFE = "咖啡馆"
    CAFE_ONLY_TOUCH = "咖啡馆只摸头"
    TIMETABLE = "课程表"
    CLUB = "社团"
    MANUFACTURE = "制造"
    STORE = "商店"
    FREE_SHOP_AWARD = "每日免费奖励"
    BUY_AP = "购买AP"
    BOUNTY = "悬赏通缉"
    SPECIAL = "特殊任务"
    SCHOOL_EXCHANGE_MEETING = "学园交流会"
    EXAM = "战术测试"
    TACTICAL_CHALLENGE = "战术大赛"
    HARD = "困难关卡"
    EVENT = "活动关卡"
    EVENTRECAP = "活动一览"
    ASSAULT = "总力战"
    DAILY = "每日任务"
    MAIL = "邮件"
    NORMAL = "普通关卡"
    ONE_CLICK_RAID = "一键扫荡"
    PUSH_NORMAL = "普通推图"
    PUSH_HARD = "困难推图"
    MAIN_STORY = "主线剧情"
    SHORT_STORY = "短篇剧情"
    SIDE_STORY = "支线剧情"
    SOLVE_CHALLENGE = "挑战任务"
    CUSTOM = "自定义任务"

class TaskInstance:
    """
    连接配置文件里的task任务名称与i18n包里对应的翻译文字key

    task_config_name: 
        配置文件里的task任务名称
    i18n_key_name:
        i18n包里的翻译文字key
    task_module:
        该task对应模块
    task_params:
        该task对应模块入参
    """
    def __init__(self, task_config_name: str, i18n_key_name: str, task_module: Task, task_params: dict):
        self.task_config_name = task_config_name
        self.i18n_key_name = i18n_key_name
        self.task_module = task_module
        self.task_params = task_params

class TaskInstanceMap:
    """
    可执行任务列表 包含所有脚本可以执行的一级任务
    """
    def __init__(self):
        self.taskmap = {
            TaskName.LOGIN_GAME:  
                TaskInstance(
                    task_config_name = TaskName.LOGIN_GAME,
                    i18n_key_name = "task_login_game",
                    task_module = EnterGame,
                    task_params = {'strict_mode': False}, # 用户手动添加的登录任务不记录资源和检查重新登录
                ),
            TaskName.MOMOTALK: TaskInstance(
                    task_config_name = TaskName.MOMOTALK,
                    i18n_key_name = "task_clear_momotalk",
                    task_module = InMomotalk,
                    task_params = {}
                ),
            TaskName.EVENTRECAP: TaskInstance(
                    task_config_name= TaskName.EVENTRECAP,
                    i18n_key_name="task_event_recap",
                    task_module=InEventRecap,
                    task_params = {}
                ),
            TaskName.CAFE: TaskInstance(
                    task_config_name = TaskName.CAFE,
                    i18n_key_name = "task_cafe",
                    task_module = InCafe,
                    task_params = {}
                ),
            TaskName.CAFE_ONLY_TOUCH: TaskInstance(
                    task_config_name = TaskName.CAFE_ONLY_TOUCH,
                    i18n_key_name = "task_cafe_deprecated",
                    task_module = InCafe,
                    task_params = {}
                ),
            TaskName.TIMETABLE: TaskInstance(
                    task_config_name = TaskName.TIMETABLE,
                    i18n_key_name = "task_timetable",
                    task_module = InTimeTable,
                    task_params = {}
                ),
            TaskName.CLUB: TaskInstance(
                    task_config_name = TaskName.CLUB,
                    i18n_key_name = "task_club",
                    task_module = InClub,
                    task_params = {}
                ),
            TaskName.MANUFACTURE: TaskInstance(
                    task_config_name = TaskName.MANUFACTURE,
                    i18n_key_name = "task_craft",
                    task_module = InCraft,
                    task_params = {}
                ),
            TaskName.STORE: TaskInstance(
                    task_config_name = TaskName.STORE,
                    i18n_key_name = "task_shop",
                    task_module = InShop,
                    task_params = {}
                ),
            TaskName.FREE_SHOP_AWARD: TaskInstance(
                    task_config_name = TaskName.FREE_SHOP_AWARD,
                    i18n_key_name = "task_daily_free_award",
                    task_module = InFreeAward,
                    task_params = {}
            ),
            TaskName.BUY_AP: TaskInstance(
                    task_config_name = TaskName.BUY_AP,
                    i18n_key_name = "task_buy_ap",
                    task_module = BuyAP,
                    task_params = {}
                ),
            TaskName.BOUNTY: TaskInstance(
                    task_config_name = TaskName.BOUNTY,
                    i18n_key_name = "task_wanted",
                    task_module = InWanted,
                    task_params = {}
                ),
            TaskName.SPECIAL: TaskInstance(
                    task_config_name = TaskName.SPECIAL,
                    i18n_key_name = "task_special",
                    task_module = InSpecial,
                    task_params = {}
                ),
            TaskName.SCHOOL_EXCHANGE_MEETING: TaskInstance(
                    task_config_name = TaskName.SCHOOL_EXCHANGE_MEETING,
                    i18n_key_name = "task_exchange",
                    task_module = InExchange,
                    task_params = {}
                ),
            TaskName.TACTICAL_CHALLENGE: TaskInstance(
                    task_config_name = TaskName.TACTICAL_CHALLENGE,
                    i18n_key_name = "task_contest",
                    task_module = InContest,
                    task_params = {'collect': False}
                ),
            TaskName.EXAM: TaskInstance(
                    task_config_name = TaskName.EXAM,
                    i18n_key_name = "task_exam",
                    task_module = InExam,
                    task_params = {}
                ),
            TaskName.ASSAULT: TaskInstance(
                    task_config_name = TaskName.ASSAULT,
                    i18n_key_name = "task_assault",
                    task_module = AutoAssault,
                    task_params = {}
                ),
            TaskName.EVENT: TaskInstance(
                    task_config_name = TaskName.EVENT,
                    i18n_key_name = "task_event",
                    task_module = InEvent,
                    task_params = {}
                ),
            TaskName.DAILY: TaskInstance(
                    task_config_name = TaskName.DAILY,
                    i18n_key_name = "task_daily",
                    task_module = CollectDailyRewards,
                    task_params = {}
                ),
            TaskName.MAIL: TaskInstance(
                    task_config_name = TaskName.MAIL,
                    i18n_key_name = "task_mail",
                    task_module = CollectMails,
                    task_params = {}
                ),
            TaskName.ONE_CLICK_RAID: TaskInstance(
                task_config_name=TaskName.ONE_CLICK_RAID,
                i18n_key_name="task_oneclick_raid",
                task_module=InQuest,
                task_params={'types': ["one-click"]}
            ),
            TaskName.NORMAL: TaskInstance(
                    task_config_name = TaskName.NORMAL,
                    i18n_key_name = "task_normal",
                    task_module = InQuest,
                    task_params = {'types': ["normal"]}
                ),
            TaskName.PUSH_NORMAL: TaskInstance(
                    task_config_name = TaskName.PUSH_NORMAL,
                    i18n_key_name = "push_normal",
                    task_module = InQuest,
                    task_params = {'types': ["push-normal"]}
                ),
            TaskName.HARD: TaskInstance(
                    task_config_name = TaskName.HARD,
                    i18n_key_name = "task_hard",
                    task_module = InQuest,
                    task_params = {'types': ["hard"]}
                ),
            TaskName.PUSH_HARD: TaskInstance(
                    task_config_name = TaskName.PUSH_HARD,
                    i18n_key_name = "push_hard",
                    task_module = InQuest,
                    task_params = {'types': ["push-hard"]}
                ),
            TaskName.MAIN_STORY: TaskInstance(
                    task_config_name = TaskName.MAIN_STORY,
                    i18n_key_name = "push_main_story",
                    task_module = AutoStory,
                    task_params = {'types': ["main"]}
                ),
            TaskName.SHORT_STORY: TaskInstance(
                    task_config_name = TaskName.SHORT_STORY,
                    i18n_key_name = "task_short_story",
                    task_module= AutoStory,
                    task_params = {'types': ["short"]}
            ),
            TaskName.SIDE_STORY: TaskInstance(
                    task_config_name = TaskName.SIDE_STORY,
                    i18n_key_name = "task_side_story",
                    task_module = AutoStory,
                    task_params = {'types': ["side"]}
            ),
            TaskName.SOLVE_CHALLENGE: TaskInstance(
                    task_config_name = TaskName.SOLVE_CHALLENGE,
                    i18n_key_name = "task_solve_challenge",
                    task_module = SolveChallenge,
                    task_params = {}
            ),
            TaskName.CUSTOM: TaskInstance(
                    task_config_name = TaskName.CUSTOM,
                    i18n_key_name = "task_user_def_task",
                    task_module = UserTask,
                    task_params = {}
                ),
        }
        # 生成config task name到i18n task name的映射表
        self.task_config_name_2_i18n_name =  {conname: config.get_text(self.taskmap[conname].i18n_key_name) for conname in self.taskmap}


task_instances_map = TaskInstanceMap()

class AllTask:

    # 单例
    def __init__(self) -> None:
        pass
        
    def parse_task(self) -> None:
        """
        从config里解析任务列表，覆盖原有的任务列表
        """
        self.taskpool = []
        if config.userconfigdict["OPEN_GAME_APP_TASK"]:
            self.add_task(EnterGame())
        # 用于保存最后一次战术大赛的任务实例
        last_contest = None
        # GUI为了显示TaskName也会导入此文件，从而创建AllTask的实例，这边判断下如果config没有解析json就跳过
        if "TASK_ORDER" in config.userconfigdict and "TASK_ACTIVATE" in config.userconfigdict:
            # 把config的任务列表转换成任务实例列表
            for i in range(len(config.userconfigdict['TASK_ORDER'])):
                task_name = config.userconfigdict['TASK_ORDER'][i]
                if task_name not in task_instances_map.taskmap:
                    logging.error({
                        CN: f"任务名:<{task_name}>无法解析, 已知的任务名有: {list(task_instances_map.taskmap.keys())}",
                        EN: f"Task name : {task_name} can not be parsed, please check it is one of: {list(task_instances_map.taskmap.keys())}"
                    })
                    raise Exception("Task Name can not be recognized and parsed")
                # 如果任务对应的TASK_ACTIVATE为False，则不添加任务
                if config.userconfigdict['TASK_ACTIVATE'][i] == False:
                    continue
                self.add_task(task_instances_map.taskmap[task_name].task_module(**task_instances_map.taskmap[task_name].task_params))
                if task_name == TaskName.TACTICAL_CHALLENGE:
                    last_contest = self.taskpool[-1]
            # 将最后一次战术大赛的收集奖励设置为True
            if last_contest:
                last_contest.set_collect(True)
        else:
            logging.warn({"zh_CN": "配置文件无TASK_ORDER和TASK_ACTIVATE解析", "en_US":"NO TASK_ORDER and TASK_ACTIVATE in config file"})
        # 任务列表末尾添加一个PostAllTask任务，用于统计资源
        if config.userconfigdict["DO_POST_ALL_TASK"]:
            self.add_task(PostAllTask())
        
        
    
    def run(self):
        """
        运行任务
        """
        # 运行任务前解析需要执行的任务内容，适应config的不同解析导致的config本身的更改
        self.parse_task()
        # 解析上次运行到第几个任务了，默认这个下标值是-1，如果是continue run的话会是发生报错时的任务下标。
        last_do_task_index = config.sessiondict["CURRENT_PERIOD_TASK_INDEX"]
        if last_do_task_index != -1:
            logging.warn(istr({
                CN: f"CURRENT_PERIOD_TASK_INDEX = {last_do_task_index}，继续运行",
                EN: f"CURRENT_PERIOD_TASK_INDEX = {last_do_task_index}, continue run"
            }))
        for i,task in enumerate(self.taskpool):
            if i < last_do_task_index and task.name != "EnterGame":
                # 跳过已经完成的任务（保留登录游戏任务）
                continue
            # 运行任务，更新正在运行的任务下标
            config.sessiondict["CURRENT_PERIOD_TASK_INDEX"] = i
            task.run()
    
    def add_task(self, task:Task) -> None:
        """
        添加任务
        """
        self.taskpool.append(task)


my_AllTask = AllTask()