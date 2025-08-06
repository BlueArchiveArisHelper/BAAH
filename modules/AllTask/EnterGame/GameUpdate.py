import json
import re
import shutil
import time
import os
import zipfile

import requests

from DATA.assets.PageName import PageName
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PopupName import PopupName

from modules.AllPage.Page import Page
from modules.AllTask.Task import Task

from modules.utils.log_utils import logging

from modules.utils import subprocess_run, click, swipe, match, page_pic, button_pic, popup_pic, sleep, check_app_running, open_app, config, screenshot, EmulatorBlockError, istr, CN, EN, match_pixel, install_apk, install_dir

class GameUpdateInfo():
    def __init__(self, apk_url, is_xapk):
        self.apk_url = apk_url
        self.is_xapk = is_xapk

# =====

class GameUpdate(Task):
    def __init__(self, name="GameUpdate", pre_times = 1, post_times = 1) -> None:
        super().__init__(name, pre_times, post_times)
        self.download_temp_folder = "DATA/tmp"
        
    def pre_condition(self) -> bool:
        return True
    
    def htmlread(url):
        if "html://" not in url:
            raise Exception("url must start with html://")
        try:
            html = requests.get(url.replace("html://", "")).text
            apk_links = re.findall(r'https://pkg.bluearchive-cn.com[^\s\'"]+?\/com.RoamingStar.BlueArchive.apk', html)
            return apk_links[0]
        except Exception as e:
            logging.error(e)
            return None
    
    def jsonread(url):
        """
        从url中获取json数据
        tips,原本想让定位也写在url中的，但是不会写。 ——By BlockHaity
        """
        if "json://" not in url:
            return Exception("url must start with json://")
        try:
            url = url.replace("json://", "")
            jsondata = json.loads(requests.get(url).text)
            return jsondata['data']['android_download_link']
        except Exception as e:
            logging.error(e)
            return None
    
    
    def aria2_download(url, filename):
        aria2c_try = 0
        while aria2c_try < config.userconfigdict["ARIA2_MAX_TRIES"]:
            logging.info({"zh_CN": f"开始下载文件: {url}, 线程数: {config.userconfigdict['ARIA2_THREADS']}, 尝试次数: {aria2c_try + 1}","en_US": f"Start downloading file: {url}, thread count: {config.userconfigdict['ARIA2_THREADS']}, try count: {aria2c_try + 1}"})
            run = subprocess_run([config.userconfigdict["ARIA2_PATH"], "-c", "-x", str(config.userconfigdict["ARIA2_THREADS"]), url, "-o", filename])
            if run.returncode != 0:
                output = str(run.stderr)
                logging.error({"zh_CN": f"下载文件失败: {url}, 错误信息: {output}",
                                         "en_US": f"Download file failed: {url}, error message: {output}"})
                aria2c_try += 1
                time.sleep(config.userconfigdict["ARIA2_FAILURED_WAIT_TIME"])
            else:
                logging.info({"zh_CN": f"下载文件成功",
                                       "en_US": f"Download file success"})
                break
        else:
            raise Exception(istr({"zh_CN": f"下载文件失败: {url}, 尝试次数: {aria2c_try + 1} 次, 超出最大尝试次数",
                                 "en_US": f"Download file failed: {url}, try count: {aria2c_try + 1}, exceed max try count"
            }))
        
    def _parse_download_link(self):
        download_info = GameUpdateInfo(apk_url = config.userconfigdict["UPDATE_API_URL"], is_xapk = True)
        if 'html://' in config.userconfigdict["UPDATE_API_URL"]:
            download_info.apk_url = GameUpdate.htmlread(config.userconfigdict["UPDATE_API_URL"])
            download_info.is_xapk = False
        elif 'json://' in config.userconfigdict["UPDATE_API_URL"]:
            download_info.apk_url = GameUpdate.jsonread(config.userconfigdict["UPDATE_API_URL"])
            download_info.is_xapk = False
        return download_info

    def _download_apk_file(self, download_info):
        if download_info.is_xapk:
            GameUpdate.aria2_download(download_info.apk_url, os.path.join(self.download_temp_folder, "update.xapk"))
            with zipfile.ZipFile(os.path.join(self.download_temp_folder, "update.xapk"), 'r') as zip_ref:
                os.mkdir(os.path.join(self.download_temp_folder, "unzip"))
                zip_ref.extractall(os.path.join(self.download_temp_folder, "unzip"))
        else:
            GameUpdate.aria2_download(download_info.apk_url, os.path.join(self.download_temp_folder, "update.apk"))

    def _install_apk_file(self, download_info):
        if download_info.is_xapk:
            install_dir(os.path.join(self.download_temp_folder, "unzip"))
        else:
            install_apk(os.path.join(self.download_temp_folder, "update.apk"))
    
    def _clear_tmp_folder(self):
        logging.info({
            "zh_CN":"更新完成，清理目录",
            "en_US": "GameUpdate completed, clean up directory"
            })
        try:
            shutil.rmtree(self.download_temp_folder)
        except Exception as e:
            logging.info({
                "zh_CN": f"清理目录{self.download_temp_folder}失败",
                "en_US": f"Failed to clean up directory {self.download_temp_folder}"
            })
            
    def on_run(self):
        # 1. 解析url
        download_info = self._parse_download_link()
        if download_info.apk_url is None:
            logging.error({
                "zh_CN": "无法获取包体更新链接，请报告给开发者",
                "en_US": "Cannot get apk update link, please report to the developer"
            })
            return

        self.task_start_time = time.time()
        logging.info({
             "zh_CN": "检测到有APP更新，开始下载更新",
             "en_US": "Detected that there is an APP update, start downloading the update"
        })
        # 如果没有下载目录，则创建
        if not os.path.exists(self.download_temp_folder):
            os.mkdir(self.download_temp_folder)
        
        # 2. 下载
        self._download_apk_file(download_info)
        
        logging.info({
            "zh_CN":"更新下载完成，开始安装",
            "en_US": "GameUpdate download completed, start installation"
        })
        
        # 3. 安装
        self._install_apk_file(download_info)
        
        # 4. 清目录
        self._clear_tmp_folder()
        
    def post_condition(self) -> bool:
        return True