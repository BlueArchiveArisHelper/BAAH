from modules.AllTask import *

from modules.AllPage.Page import Page

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, screenshot
from modules.utils.log_utils import logging
from modules.configs.MyConfig import config

# 用户config里的 任务名称 和 任务类 的对应关系
task_dict= {
    "登录游戏":[EnterGame,{}],
    "清momotalk":[InMomotalk,{}],
    "咖啡馆":[InCafe,{}],
    "咖啡馆只摸头":[InCafe,{}], # 此方法弃用，现在所有咖啡馆参数通过config调整
    "课程表":[InTimeTable,{}],
    "社团":[InClub,{}],
    "商店":[InShop,{}],
    "悬赏通缉":[InWanted,{}],
    "特殊任务":[InSpecial,{}],
    "学园交流会":[InExchange,{}],
    "战术大赛":[InContest, {'collect':False}],
    "战术大赛只领奖":[InContest, {'onlyFirst':True}],
    "总力战":[AutoAssault,{}],
    "困难关卡":[InQuest, {'types':["hard"]}],
    "活动关卡":[InEvent,{}],
    "每日任务":[CollectDailyRewards,{}],
    "邮件":[CollectMails,{}],
    "普通关卡":[InQuest, {'types':["normal"]}],
    "普通推图":[InQuest, {'types':["push-normal"]}],
    "困难推图":[InQuest, {'types':["push-hard"]}],
    "主线剧情":[AutoStory,{}],
    "购买AP":[BuyAP,{}],
}

class AllTask:

    # 单例
    def __init__(self) -> None:
        self.parse_task()
        
    def parse_task(self) -> None:
        """
        从config里解析任务列表，覆盖原有的任务列表
        """
        self.taskpool = []
        # 用于保存最后一次战术大赛的任务实例
        last_contest = None
        # GUI之前会运行到这里，所以这里需要判断一下
        if config.userconfigdict["TASK_ORDER"] and config.userconfigdict["TASK_ACTIVATE"]:
            # 把config的任务列表转换成任务实例列表
            for i in range(len(config.userconfigdict['TASK_ORDER'])):
                task_name = config.userconfigdict['TASK_ORDER'][i]
                if task_name not in task_dict:
                    raise Exception(f"任务名:<{task_name}>不存在, 请检查config.py中的TASK_ORDER是否正确, 正确的任务名有: {list(task_dict.keys())}")
                # 如果任务对应的TASK_ACTIVATE为False，则不添加任务
                if config.userconfigdict['TASK_ACTIVATE'][i] == False:
                    continue
                self.add_task(task_dict[task_name][0](**task_dict[task_name][1]))
                if task_name == "战术大赛":
                    last_contest = self.taskpool[-1]
            # 将最后一次战术大赛的收集奖励设置为True
            if last_contest:
                last_contest.set_collect(True)
        else:
            logging.error({"zh_CN": "配置文件严重错误，请删除config.json后打开GUI.exe生成config.py文件或进群询问", "en_US":"Serious error in config file, please delete config.json and open GUI.exe to generate config.py file or ask in the group"})
        # 任务列表末尾添加一个PostAllTask任务，用于统计资源
        self.add_task(PostAllTask())
        
        
    
    def run(self):
        """
        运行任务
        """
        for task in self.taskpool:
            task.run()
    
    def add_task(self, task:Task) -> None:
        """
        添加任务
        """
        self.taskpool.append(task)


my_AllTask = AllTask()