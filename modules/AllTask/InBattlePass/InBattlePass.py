
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, screenshot, match_pixel, istr, CN, EN, JP, is_server_type_in_group, MultiServerType, get_correct_asset, AssetMappingKeys
from modules.utils.log_utils import logging

class InBattlePass(Task):
    def __init__(self, name="InBattlePass") -> None:
        super().__init__(name)
        self.enter_battlepass_xy = (396, 550)
        self.enter_task_list_xy = (394, 650)
        self.back_to_battlepass_xy = (41, 39)
        self.back_to_home_xy = (1242, 43)

        self.collect_reward_xy = (1158, 647)
        self.activate_collected_reward_bgr = ((70, 200, 250),(80, 213, 260))

     
    def pre_condition(self) -> bool:
        return self.back_to_home()

    def __collect_battle_pass_reward(self) -> None:
        success_collect = self.run_until(
            lambda: click(self.collect_reward_xy),
            lambda: not match_pixel(self.collect_reward_xy, self.activate_collected_reward_bgr),
            times=3
        )
        if success_collect:
            logging.info(istr({
                CN: f"领取战斗通行证奖励成功",
                EN: f"Successfully collected Battle Pass reward",
            }))
        return success_collect

    def __from_battle_pass_to_home(self) -> None:
        return self.run_until(
            lambda: click(self.back_to_home_xy),
            lambda: match(page_pic(PageName.PAGE_HOME)),
            times=3
        )
     
    def on_run(self) -> None:
        # 进入通行证页面
        has_enter_battle_pass = self.run_until(
            lambda: click(self.enter_battlepass_xy),
            lambda: match(page_pic(PageName.PAGE_BATTLE_PASS)),
            times=3
        )
        if not has_enter_battle_pass:
            logging.warn(istr({
                CN: f"尝试进入战斗通行证页面失败，跳过任务",
                EN: f"Failed to enter the Battle Pass page, skipping task",
            }))
        # 进入左下角领奖励页面
        enter_collect_reward_page = self.run_until(
            lambda: click(self.enter_task_list_xy),
            lambda: match(page_pic(PageName.PAGE_BATTLE_PASS_CENTER)),
            times=3
        )
        if enter_collect_reward_page:
            logging.info(istr({
                CN: f"进入战斗通行证领奖励页面",
                EN: f"Enter the Battle Pass reward page",
            }))
            self.__collect_battle_pass_reward()
            # 返回战斗通行证页面
            self.run_until(
                click(self.back_to_battlepass_xy),
                lambda: match(page_pic(PageName.PAGE_BATTLE_PASS)),
                times=3
            )
        # 领取进度奖励
        self.__collect_battle_pass_reward()
        # 返回主页面
        self.__from_battle_pass_to_home()

     
    def post_condition(self) -> bool:
        return self.back_to_home()