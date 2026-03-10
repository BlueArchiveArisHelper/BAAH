
from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils import click, swipe, match, page_pic, button_pic, popup_pic, sleep, ocr_area, config, ActionType,screenshot, match_pixel, istr, CN, EN
from modules.utils.log_utils import logging
import time, re

class PostAllTask(Task):
    def __init__(self, name="PostAllTask") -> None:
        super().__init__(name)

     
    def pre_condition(self) -> bool:
        return self.back_to_home()
    
    def save_sources_to_user_storage(self, rec_obj):
        """记录钻石信用币到用户存储"""
        # 记录时间 年月日
        str_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        # 增加时间戳
        rec_obj["date"] = str_time
        # 检查上次存储的时间
        last_rec_date = config.userstoragedict.get("LAST_SAVE_MONEY_DIAMOND_DATE", "")
        if last_rec_date != str_time:
            # 如果不是同一天，更新存储的时间
            config.update_user_storage_dict(
                "LAST_SAVE_MONEY_DIAMOND_DATE", 
                str_time, 
                action_type=ActionType.WRITE)
            # 更新存储的资源
            config.update_user_storage_dict(
                "HISTORY_MONEY_DIAMOND_LIST", 
                rec_obj, 
                action_type=ActionType.APPEND)
            # 保存json
            config.save_user_storage_dict()

            logging.info(istr({
                CN: f"记录资源到用户存储成功 {rec_obj}",
                EN: f"Successfully saved resources to user storage {rec_obj}"
            }))
        else:
            logging.info(istr({
                CN: f"今天已经记录资源信息过了, 不再保存 {rec_obj}",
                EN: f"Already saved record today, not saving again {rec_obj}"
            }))
        
    
    def record_resources(self):
        """
        记录主页中的资源
        """
        resources = self.ocr_account_resource()
        logging.info(istr({
            CN: f"退出游戏时OCR到的资源信息 {resources}",
            EN: f"OCR result of resources when exiting the game {resources}"
        }))

        # 检查OCR结果是否合法
        if re.fullmatch(r'\d+/\d+', resources["power"]) is not None and re.fullmatch(r'\d{1,3}(,\d{3})*', resources["credit"]) is not None and re.fullmatch(r'\d{1,3}(,\d{3})*', resources["diamond"]) is not None:
            config.sessiondict["AFTER_BAAH_SOURCES"] = resources

            try:
                self.save_sources_to_user_storage(resources)
            except Exception as e:
                logging.error(istr({
                    CN: f"保存资源到用户存储失败: {e}",
                    EN: f"Failed to save resources to user storage: {e}"
                }))
        else:
            logging.warn({"zh_CN": "退出游戏时，资源数量OCR非法格式，跳过记录", "en_US": "Invalid resource OCR result when exiting the game, skipping"})
     
    def on_run(self) -> None:
        self.record_resources()

     
    def post_condition(self) -> bool:
        return self.back_to_home()