import json
import re
import shutil
import time
import os
import zipfile
from urllib.request import urlretrieve
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl
import socket

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
    api_urls = {
        "JP":[
            "https://baah.hitfun.top/apk/jp",
            "https://api.blockhaity.qzz.io/baapk/jp",
            "https://blockhaity-api.netlify.app/baapk/jp"
        ],
        "GLOBAL":[
            "https://baah.hitfun.top/apk/global",
            "https://api.blockhaity.qzz.io/baapk/global",
            "https://blockhaity-api.netlify.app/baapk/global"
        ],
        "CN":"html://https://mumu.163.com/games/22367.html",
        "CN_BILI": "json://https://line1-h5-pc-api.biligame.com/game/detail/gameinfo?game_base_id=109864"
    }

    direct_get_urls = [
        "https://api.blockhaity.qzz.io/api/baapk.json",
        "https://blockhaity-api.netlify.app/api/baapk.json"
    ]
    
    def __init__(self, name="GameUpdate", pre_times = 1, post_times = 1) -> None:
        super().__init__(name, pre_times, post_times)
        self.download_temp_folder = "DATA/tmp"
    
    def pre_condition(self) -> bool:
        return True
    
    def get_final_url(url, timeout=10, retry_count=3):
        """
        获取URL重定向后的最终链接
    
        参数:
            url (str): 要检查的URL
            timeout (int): 请求超时时间(秒)
            retry_count (int): 失败重试次数
        
        返回:
            str: 最终URL或None(如果失败)
        """
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
        # 尝试多次请求
        for attempt in range(retry_count):
            try:
                # 创建请求对象
                request = Request(url, headers=headers)
            
                # 创建SSL上下文，用于处理HTTPS
                context = ssl.create_default_context()
            
                # 打开URL，设置超时和SSL上下文
                # urllib默认会处理重定向，不需要额外设置
                response = urlopen(request, timeout=timeout, context=context)

                # 获取最终URL和状态码
                final_url = response.geturl()
                status_code = response.getcode()
               
                logging.debug(f"请求成功，状态码: {status_code}")
                logging.debug(f"最终URL: {final_url}")
            
                return final_url
            
            except HTTPError as e:
                logging.debug(f"HTTP错误: {e.code} {e.reason}")
            
                # 对于HTTP错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logging.debug(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except URLError as e:
                # 处理URL错误，包括DNS解析失败
                logging.debug(f"URL错误: {e.reason}")
            
                # 检查是否是DNS解析错误
                if isinstance(e.reason, socket.gaierror) and "Name or service not known" in str(e.reason):
                    logging.debug("\n检测到DNS解析问题")

                    # 对于DNS错误，不再重试
                    return None
                
                # 对于其他URL错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logging.debug(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except socket.timeout as e:
                logging.debug(f"请求超时: {e}")
            
                # 对于超时错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logging.debug(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except Exception as e:
                logging.debug(f"发生错误: {e}")
            
                # 对于其他异常，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logging.debug(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None

    
    def htmlread(url):
        if "html://" not in url:
            raise Exception("url must start with html://")
        try:
            html = requests.get(url.replace("html://", "")).text
            # apk_links = re.findall(r'https://pkg.bluearchive-cn.com[^\s\'"]+?\/com.RoamingStar.BlueArchive.apk', html)
            # mumu网页上游变动，故修改。
            apk_links = re.findall(r'https://mumu-apk.fp.ps.netease.com/file[^\s\'"]+?.apk', html)
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
    
    
    def aria2_download(url, name, filename):
        aria2c_try = 0
        while aria2c_try < config.userconfigdict["ARIA2_MAX_TRIES"]:
            logging.info({"zh_CN": f"开始从{name}下载文件: , 线程数: {config.userconfigdict['ARIA2_THREADS']}, 尝试次数: {aria2c_try + 1}",
                                    "en_US": f"Start downloading file form {name} : , thread count: {config.userconfigdict['ARIA2_THREADS']}, try count: {aria2c_try + 1}"})
            run = subprocess_run([config.userconfigdict["ARIA2_PATH"], "-c", "-x", str(config.userconfigdict["ARIA2_THREADS"]), url, "-o", filename])
            if run.returncode != 0:
                output = str(run.stderr)
                logging.error({"zh_CN": f"从{name}下载文件失败, 错误信息: {output}",
                                         "en_US": f"Download file failed from {name}, error message: {output}"})
                aria2c_try += 1
                time.sleep(config.userconfigdict["ARIA2_FAILURED_WAIT_TIME"])
            else:
                logging.info({"zh_CN": f"下载文件成功",
                                       "en_US": f"Download file success"})
                break
        else:
            raise Exception(istr({"zh_CN": f"从{name}下载文件失败, 尝试次数: {aria2c_try + 1} 次, 超出最大尝试次数",
                                 "en_US": f"Download file failed from {name}, try count: {aria2c_try + 1}, exceed max try count"
            }))
        
    def urlretrieve_download(url, name, filename):
        urlretrieve_try = 0
        while urlretrieve_try < config.userconfigdict["URLRETRIEVE_MAX_TRIES"]:
            try:
                logging.info({"zh_CN": f"开始从{name}下载文件, 尝试次数: {urlretrieve_try + 1}"})
                logging.warn({"zh_CN": "你正在使用urlretrieve下载，此工具仅支持单线程下载。",
                                        "en_US": "You are using urlretrieve to download, this tool only supports single-threaded download."})
                urlretrieve(url, filename)
                logging.info({"zh_CN": f"下载文件成功",
                                       "en_US": f"Download file success"})
                break
            except Exception as e:
                logging.error({"zh_CN": f"从{name}下载文件失败, 错误信息: {e}",
                                        "en_US": f"Download file failed from {name}, error message: {e}"})
                aria2c_try += 1
                time.sleep(config.userconfigdict["ARIA2_FAILURED_WAIT_TIME"])
        else:
            raise Exception(istr({"zh_CN": f"从{name}下载文件失败, 尝试次数: {urlretrieve_try + 1} 次, 超出最大尝试次数",
                                              "en_US": f"Download file failed from {name}, try count: {urlretrieve_try + 1}, exceed max try count"}))
        
    def _parse_download_link_api(self):
        download_info = GameUpdateInfo(apk_url = None, is_xapk = None)
        if config.userconfigdict['SERVER_TYPE'] == 'JP':
            download_info.is_xapk = True
            download_info.apk_url = GameUpdate.api_urls['JP']
        elif (config.userconfigdict['SERVER_TYPE'] == 'GLOBAL_EN'
               or config.userconfigdict['SERVER_TYPE'] == 'GLOBAL'):
            download_info.is_xapk = True
            download_info.apk_url = GameUpdate.api_urls['GLOBAL']
        elif config.userconfigdict['SERVER_TYPE'] == 'CN':
            download_info.is_xapk = False
            download_info.apk_url = GameUpdate.htmlread(GameUpdate.api_urls['CN'])
        elif config.userconfigdict['SERVER_TYPE'] == 'CN_BILI':
            download_info.is_xapk = False
            download_info.apk_url = GameUpdate.jsonread(GameUpdate.api_urls['CN_BILI'])
        else:
            download_info = None
        # 之前通过链接判断有误判风险，故改为通过配置文件判断是否为xapk
        # if 'html://' in config.userconfigdict["UPDATE_API_URL"]:
        #     download_info.apk_url = GameUpdate.htmlread(config.userconfigdict["UPDATE_API_URL"])
        #     download_info.is_xapk = False
        # elif 'json://' in config.userconfigdict["UPDATE_API_URL"]:
        #     download_info.apk_url = GameUpdate.jsonread(config.userconfigdict["UPDATE_API_URL"])
        #     download_info.is_xapk = False
        return download_info

    def _parse_download_link_direct_get(self):
        number = 1
        for url in GameUpdate.direct_get_urls:
            try:
                logging.info(istr({"zh_CN": f"尝试从节点{number}获取更新链接 ", "en_US": f"Trying to get update link from node {number}"}))
                data = json.loads(requests.get(url).text)
                break
            except Exception as e:
                if number == len(GameUpdate.direct_get_urls):
                    logging.error(e)
                    raise Exception(istr({
                        "zh_CN": "无法获取更新链接，请检查网络",
                        "en_US": "Failed to get update link, please check your network"
                    }))
                elif number < len(GameUpdate.direct_get_urls):
                    logging.error(e)
                    logging.error(istr({
                        "zh_CN": "获取更新链接失败，从其他节点重试",
                        "en_US": "Failed to get update link, retry from other nodes"
                    }))
                    number += 1
        download_info = GameUpdateInfo(apk_url = None, is_xapk = None)
        if config.userconfigdict['SERVER_TYPE'] == 'JP':
            download_info.apk_url = data['jp']
            download_info.is_xapk = True
        elif (config.userconfigdict['SERVER_TYPE'] == 'GLOBAL_EN'
               or config.userconfigdict['SERVER_TYPE'] == 'GLOBAL'):
            download_info.apk_url = data['global']
            download_info.is_xapk = True
        elif config.userconfigdict['SERVER_TYPE'] == 'CN':
            download_info.apk_url = data['cn']
            download_info.is_xapk = False
        elif config.userconfigdict['SERVER_TYPE'] == 'CN_BILI':
            download_info.apk_url = data['cn_bili']
            download_info.is_xapk = False
        else:
            download_info = None
        return download_info
        
    def _download_apk_file_api(self, download_info):
        if download_info.is_xapk is True:
            try_download = 1
            for apk_url in download_info.apk_url:
                try:
                    if config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "aria2":
                        GameUpdate.aria2_download(apk_url, istr({"zh_CN":"API节点 ","en_US":"API Node "}) + str(try_download),os.path.join(self.download_temp_folder, "update.xapk"))
                    elif config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "urlretrieve":
                        final_url = GameUpdate.get_final_url(apk_url)
                        GameUpdate.urlretrieve_download(final_url, istr({"zh_CN":"API节点 ","en_US":"API Node "}) + str(try_download),os.path.join(self.download_temp_folder, "update.xapk"))
                    else:
                        logging.warn(istr({
                            "zh_CN": "未知的下载器，使用aria2下载",
                            "en_US": "Unknown downloader, use aria2 to download"
                        }))
                        GameUpdate.aria2_download(apk_url, istr({"zh_CN":"API节点 ","en_US":"API Node "}) + str(try_download),os.path.join(self.download_temp_folder, "update.xapk"))
                    break
                except Exception as e:
                    if try_download == len(download_info.apk_url):
                        raise Exception(istr({
                            "zh_CN": "无法下载更新，请检查网络",
                            "en_US": "Failed to download update, please check your network"
                        }))
                    else:
                        logging.error(e)
                        logging.error(istr({
                            "zh_CN": "下载失败,从其他节点重试",
                            "en_US": "Download failed, retry from other nodes"
                        }))
                        try_download += 1
                        continue
            with zipfile.ZipFile(os.path.join(self.download_temp_folder, "update.xapk"), 'r') as zip_ref:
                os.mkdir(os.path.join(self.download_temp_folder, "unzip"))
                zip_ref.extractall(os.path.join(self.download_temp_folder, "unzip"))
        elif download_info.is_xapk is False:
            if config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "aria2":
                GameUpdate.aria2_download(download_info.apk_url,"API", os.path.join(self.download_temp_folder, "update.apk"))
            elif config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "urlretrieve":
                GameUpdate.urlretrieve_download(download_info.apk_url,"API", os.path.join(self.download_temp_folder, "update.apk"))
            else:
                logging.error({"zh_CN": "未知的下载器类型", "en_US": "Unknown downloader type"})
                logging.info({"zh_CN": "使用aria2下载器", "en_US": "Using aria2 downloader"})
                GameUpdate.aria2_download(download_info.apk_url,"API", os.path.join(self.download_temp_folder, "update.apk"))
        else:
            raise Exception(istr({
                "zh_CN": "无法获取包体更新链接，请报告给开发者",
                "en_US": "Cannot get apk update link, please report to the developer"
            }))
            
    def _download_apk_file_direct_get(self, download_info):
        if download_info.is_xapk is True:
            if config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "aria2":
                GameUpdate.aria2_download(download_info.apk_url, "DirectGet", os.path.join(self.download_temp_folder, "update.xapk"))
            elif config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "urlretrieve":
                GameUpdate.urlretrieve_download(download_info.apk_url, "DirectGet", os.path.join(self.download_temp_folder, "update.xapk"))
            else:
                logging.warn(istr({
                    "zh_CN": "未知的下载器，使用aria2下载",
                    "en_US": "Unknown downloader, use aria2 to download"
                }))
                GameUpdate.aria2_download(download_info.apk_url, "DirectGet", os.path.join(self.download_temp_folder, "update.xapk"))
            with zipfile.ZipFile(os.path.join(self.download_temp_folder, "update.xapk"), 'r') as zip_ref:
                os.mkdir(os.path.join(self.download_temp_folder, "unzip"))
                zip_ref.extractall(os.path.join(self.download_temp_folder, "unzip"))
        elif download_info.is_xapk is False:
            if config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "aria2":
                GameUpdate.aria2_download(download_info.apk_url, "DirectGet", os.path.join(self.download_temp_folder, "update.apk"))
            elif config.userconfigdict["BIG_UPDATE_DOWNLOADER"] == "urlretrieve":
                GameUpdate.urlretrieve_download(download_info.apk_url, "DirectGet", os.path.join(self.download_temp_folder, "update.apk"))
            else:
                logging.error({"zh_CN": "未知的下载器类型", "en_US": "Unknown downloader type"})
        else:
            raise Exception(istr({
                "zh_CN": "无法获取包体更新链接，请报告给开发者",
                "en_US": "Cannot get apk update link, please report to the developer"
            }))
    
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
        if config.userconfigdict["BIG_UPDATE_TYPE"] == "API":
            download_info = self._parse_download_link_api()
            if download_info.apk_url is None:
                logging.error({
                    "zh_CN": "无法获取包体更新链接，请报告给开发者",
                    "en_US": "Cannot get apk update link, please report to the developer"
                })
                return
        elif config.userconfigdict["BIG_UPDATE_TYPE"] == "DIRECT_GET":
            download_info = self._parse_download_link_direct_get()
            if download_info.apk_url is None:
                logging.error({
                    "zh_CN": "无法获取包体更新链接，请报告给开发者",
                    "en_US": "Cannot get apk update link, please report to the developer"
                })

        self.task_start_time = time.time()
        logging.info({
             "zh_CN": "检测到有APP更新，开始下载更新",
             "en_US": "Detected that there is an APP update, start downloading the update"
        })
        # 如果没有下载目录，则创建
        if not os.path.exists(self.download_temp_folder):
            os.mkdir(self.download_temp_folder)
        
        # 2. 下载
        if config.userconfigdict["BIG_UPDATE_TYPE"] == "API":
            self._download_apk_file_api(download_info)
        elif config.userconfigdict["BIG_UPDATE_TYPE"] == "DIRECT_GET":
            self._download_apk_file_direct_get(download_info)
        
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
