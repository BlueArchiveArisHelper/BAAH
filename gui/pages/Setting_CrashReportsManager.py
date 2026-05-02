import os
import zipfile
import shutil

from nicegui import ui
from ..define import gui_shared_config

def get_report_list(filename):
    if not os.path.exists(gui_shared_config.CRASH_REPORT_FOLDER):
        os.mkdir(gui_shared_config.CRASH_REPORT_FOLDER)
    arr = [i for i in os.listdir(gui_shared_config.CRASH_REPORT_FOLDER) if filename in i]
    arr.sort()
    return arr

def download_report(report):
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

def refresh_report_list(container, config):
    container.clear()
    with container:
        for report in get_report_list("crash_report"):
            with ui.row().classes("flex items-center"):
                with ui.card().props('flat bordered').style("border-radius: 5; border-color: gray;"):
                    ui.label(report).style("font-size: large;")
                ui.button(gui_shared_config.get_text("button_download"), on_click=lambda _, r=report: download_report(r))
                ui.button(gui_shared_config.get_text("button_delete"), on_click=lambda _, r=report: (shutil.rmtree(os.path.join(gui_shared_config.CRASH_REPORT_FOLDER, r)), container.update()))

def Set_Crash_Report_Manager(config):
    ui.link_target("Crash_Report_Manager")
    with ui.row().classes("items-center"):
        ui.label(config.get_text("setting_crash_report_manager")).style("font-size: x-large")
        ui.button(icon="refresh", on_click=lambda: refresh_report_list(report_container, config)).props("flat round")
    
    report_container = ui.column().classes("w-full")
    refresh_report_list(report_container, config)
