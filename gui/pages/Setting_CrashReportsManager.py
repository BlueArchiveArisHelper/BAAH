import os
import zipfile
import shutil

from nicegui import ui
from ..define import gui_shared_config

def get_report_list():
    """获取崩溃报告列表，返回包含filename_key的文件夹名称的列表"""
    if not os.path.exists(gui_shared_config.CRASH_REPORT_FOLDER):
        os.mkdir(gui_shared_config.CRASH_REPORT_FOLDER)
    arr = [i for i in os.listdir(gui_shared_config.CRASH_REPORT_FOLDER)]
    arr.sort()
    return arr

def download_report(report):
    """压缩对应report文件夹下文件，并gui触发下载压缩包"""
    #TODO: 下载网页模板
    
    report_path = os.path.join(gui_shared_config.CRASH_REPORT_FOLDER, report)
    files = os.listdir(report_path)
    if not os.path.exists(gui_shared_config.TMP_FOLDER):
        os.mkdir(gui_shared_config.TMP_FOLDER)
    zip_path = os.path.join(gui_shared_config.TMP_FOLDER, report + ".zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            file_path = os.path.join(report_path, file)
            if os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))
    ui.download(zip_path, report + ".zip")

@ui.refreshable
def report_list_gui(config):
    """GUI的崩溃报告列表组件"""
    with ui.column().classes("w-full"):
        for report in get_report_list():
            with ui.row().classes("flex items-center"):
                with ui.card().props('flat bordered').style("border-radius: 5; border-color: gray;"):
                    ui.label(report).style("font-size: large;")
                ui.button(config.get_text("button_download"), on_click=lambda _, r=report: download_report(r))
                ui.button(config.get_text("button_delete"), on_click=lambda _, r=report: (shutil.rmtree(os.path.join(gui_shared_config.CRASH_REPORT_FOLDER, r)), report_list_gui.refresh()))

def Set_Crash_Report_Manager(config):
    """崩溃报告管理界面"""
    ui.link_target("Crash_Report_Manager")
    with ui.row().classes("items-center"):
        ui.label(config.get_text("setting_crash_report_manager")).style("font-size: x-large")
        ui.button(icon="refresh", on_click=lambda: report_list_gui.refresh()).props("flat round")
    
    ui.checkbox(config.get_text("config_crash_report")).bind_value(gui_shared_config.softwareconfigdict, "ENABLE_CRASH_REPORT")
    
    
    report_list_gui(config)
