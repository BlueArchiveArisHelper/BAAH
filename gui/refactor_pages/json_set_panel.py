from enum import Enum

from ..components.exec_arg_parse import get_token
from ..components.manage_baah_in_gui import run_baah_task_and_bind_log, stop_baah_task
from ..components.running_task_pool import RunningBAAHProcess_instance
from ..pages.Setting_BAAH import set_BAAH
from ..pages.Setting_Craft import set_craft
from ..pages.Setting_cafe import set_cafe
from ..pages.Setting_Login import set_login
from ..pages.Setting_emulator import set_emulator
from ..pages.Setting_event import set_event
from ..pages.Setting_exchange import set_exchange
from ..pages.Setting_hard import set_hard
from ..pages.Setting_normal import set_normal
from ..pages.Setting_other import set_other
from ..pages.Setting_server import set_server
from ..pages.Setting_shop import set_shop
from ..pages.Setting_special import set_special
from ..pages.Setting_exam import set_exam
from ..pages.Setting_task_order import set_task_order 
from ..pages.Setting_timetable import set_timetable
from ..pages.Setting_wanted import set_wanted
from ..pages.Setting_notification import set_notification
from ..pages.Setting_vpn import set_vpn
from ..pages.Setting_Assault import set_assault
from ..pages.Setting_BuyAP import set_buyAP
from ..pages.Setting_UserTask import set_usertask
from ..pages.Setting_explore import set_explore
from ..pages.Setting_Oneclick_Raid import set_oneclick_raid
from ..pages.Setting_quick_runtask import set_quick_runtask
from modules.AllTask.myAllTask import task_instances_map 
from modules.configs.MyConfig import MyConfigger
from modules.utils import _is_PC_app
from modules.configs.settingMaps import server2pic, server2activity, server2respond
from ..define import gui_shared_config
from define_actions.basic_objects import FlowActionGroup

from nicegui import ui, app, run
from typing import Callable, Optional
import os
import time

class ConfigPanelType(Enum):
    BAAH_Bsic_Settings = 0
    Daily_Task_Settings = 1
    Quick_Task_Settings = 2

panel_types_2_str = {
    ConfigPanelType.BAAH_Bsic_Settings: "BAAH基础设置",
    ConfigPanelType.Daily_Task_Settings: "日常任务设置",
    ConfigPanelType.Quick_Task_Settings: "快速任务设置"
}

class ConfigPanel:
    """
    连接子页面的i18n名称 与 渲染页面的函数

    Parameters
    ==========
    nameID: str
        子页面标题的i18n的key 或 标题名
    func: 
        子页面渲染函数
    desc:
        子页面说明渲染函数 (lambda)
    lst_config: Config
        传入时通过nameID找到对应i18n名字作为name，为None时name=nameID
    panel_types
        该配置项所属的类型列表，决定在不同的 Tab 栏目下是否显示
    """
    def __init__(self, nameID: str, func: Callable[[], None], desc: Callable[[], None] = None, i18n_config=None, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]):
        self.name = i18n_config.get_text(nameID) if i18n_config else nameID
        self.func = func
        # 4. Mock description as requested
        self.desc = desc if desc else lambda: ui.label(f"配置项 {self.name} 的详细说明及注意事项。")
        self.nameID = nameID
        self.panel_types = panel_types

def parse_obj_in_config(inconfig, obj_dict, backward = False):
    """
    将配置中的部分字段解析为实际对象，放入obj_dict

    当backward=True时，执行反向操作，将obj_dict中的对象转为json存入配置中
    """
    parse_mapping = {
        "OBJ_ACTIONS_VPN_START": lambda x: FlowActionGroup().load_from_dict(x),
        "OBJ_ACTIONS_VPN_SHUT": lambda x: FlowActionGroup().load_from_dict(x),
        "OBJ_USER_DEFINE_TASK": lambda x: FlowActionGroup().load_from_dict(x),
        "OBJ_FLOW_WHEN_LOGIN": lambda x: FlowActionGroup().load_from_dict(x),
    }
    reverse_mapping = {
        "OBJ_ACTIONS_VPN_START": lambda x:x.to_json_dict(),
        "OBJ_ACTIONS_VPN_SHUT": lambda x:x.to_json_dict(),
        "OBJ_USER_DEFINE_TASK": lambda x:x.to_json_dict(),
        "OBJ_FLOW_WHEN_LOGIN": lambda x:x.to_json_dict(),
    }
    if not backward:# json转对象，存obj_dict
        for key, clsa in parse_mapping.items():
            if key in inconfig.userconfigdict:
                obj_dict[key] = clsa(inconfig.userconfigdict[key])
    else:
        for key, clsa in reverse_mapping.items(): # 对象转json，存userconfigdict
            if key in obj_dict:
                inconfig.userconfigdict[key] = clsa(obj_dict[key])

def get_config_list(lst_config: MyConfigger, logArea, parsed_obj_dict) -> list:
    return [
        ConfigPanel("BAAH", lambda: set_BAAH(lst_config, gui_shared_config), i18n_config=None, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]),
        ConfigPanel("setting_server", lambda: set_server(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]),
        ConfigPanel("setting_emulator", lambda: set_emulator(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]),
        ConfigPanel("setting_other", lambda: set_other(lst_config, gui_shared_config), i18n_config=lst_config, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]),

        ConfigPanel("setting_task_order", lambda: set_task_order(lst_config, task_instances_map.task_config_name_2_i18n_name, logArea), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("setting_vpn", lambda: set_vpn(lst_config, parsed_obj_dict), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("setting_notification", lambda: set_notification(lst_config, gui_shared_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_login_game", lambda: set_login(lst_config, parsed_obj_dict), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_cafe", lambda: set_cafe(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_timetable", lambda: set_timetable(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_craft", lambda: set_craft(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_shop", lambda: set_shop(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_buy_ap", lambda: set_buyAP(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_wanted", lambda: set_wanted(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_special", lambda: set_special(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_exchange", lambda: set_exchange(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_exam", lambda: set_exam(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_event", lambda: set_event(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_assault", lambda: set_assault(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_oneclick_raid", lambda: set_oneclick_raid(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_hard", lambda: set_hard(lst_config, gui_shared_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_normal", lambda: set_normal(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("setting_explore", lambda: set_explore(lst_config, task_instances_map.task_config_name_2_i18n_name, logArea), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),
        ConfigPanel("task_user_def_task", lambda: set_usertask(lst_config, parsed_obj_dict), i18n_config=lst_config, panel_types = [ConfigPanelType.Daily_Task_Settings]),

        ConfigPanel("config_quick_call_task", lambda: set_quick_runtask(lst_config, task_instances_map.task_config_name_2_i18n_name, logArea), i18n_config=lst_config, panel_types = [ConfigPanelType.Quick_Task_Settings]),
        
    ]

# ---------- 页面主函数 ----------
@ui.page('/panel/{json_file_name}')
def show_json_panel(json_file_name: str):

    # Dark mode setup
    dark = ui.dark_mode()
    # Check browser preference
    is_dark = ui.run_javascript('window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches')
    if is_dark:
        dark.enable()
    else:
        dark.disable()

    # 0. Setup and Parse same as old file
    obj_parsed_dict_of_config = {}
    if get_token() is not None and get_token() != app.storage.user.get("token"):
        return
    curr_config: MyConfigger = MyConfigger()
    curr_config.parse_user_config(json_file_name)
    parse_obj_in_config(curr_config, obj_parsed_dict_of_config)

    # Styles
    ui.add_head_html('''
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                margin: 0;
                padding: 0;
                overflow: hidden; 
            }
            ::-webkit-scrollbar {
                display: none;
            }
            .section-title { 
                font-size: 16px; 
                font-weight: 600; 
                margin-bottom: 10px; 
            }
            .item-selected {
                border-left: 4px solid #1976d2;
            }
        </style>
    ''')
    
    # 3. Ratio constant
    COLUMN_RATIOS = [1, 4, 2] # Left:Middle:Right
    
    # Placeholders for controls that need to be accessed
    logArea = None
    
    # State for selected panel
    current_panel = None
    config_choose_list = []
    current_tab_type = ConfigPanelType.BAAH_Bsic_Settings

    # Refreshable areas
    @ui.refreshable
    def render_task_list():
        with ui.column().classes('w-full gap-0'):
            # Filter config list based on current tab
            filtered_list = [p for p in config_choose_list if current_tab_type in p.panel_types]
            
            for panel in filtered_list:
                is_selected = (panel == current_panel)
                base_classes = 'w-full p-3 cursor-pointer transition-colors border-b border-gray-100'
                if is_selected:
                    base_classes += ' item-selected'
                
                # Bind panel using default arg to capture loop variable
                with ui.row().classes(base_classes).on('click', lambda _, p=panel: select_panel(p)):
                    ui.label(panel.name).classes('flex-grow text-sm font-medium' if not is_selected else 'flex-grow text-sm font-bold')
                    if is_selected:
                        ui.icon('chevron_right', color='primary')

    @ui.refreshable
    def render_config_area():
        if current_panel:
            with ui.column().classes('w-full h-full p-4 overflow-y-auto'):
                ui.label(current_panel.name).classes('section-title mb-4 border-b pb-2 w-full')
                current_panel.func()
    
    @ui.refreshable
    def render_description():
        if current_panel:
            with ui.column().classes('w-full h-full p-4 overflow-y-auto'):
                 ui.label("任务说明").classes('section-title')
                 current_panel.desc()

    def select_panel(panel):
        nonlocal current_panel
        current_panel = panel
        render_task_list.refresh()
        render_config_area.refresh()
        render_description.refresh()

    # Save logic
    def perform_save():
        parse_obj_in_config(curr_config, obj_parsed_dict_of_config, backward=True)
        curr_config.save_user_config(json_file_name)
        curr_config.save_software_config()
        gui_shared_config.save_software_config()
    
    def save_and_alert():
        perform_save()
        ui.notify(curr_config.get_text("notice_save_success"))

    def run_in_terminal():
        perform_save()
        ui.notify(curr_config.get_text("notice_start_run"))
        os.system(f'start BAAH.exe "{json_file_name}"')
        
    async def run_in_gui():
        perform_save()
        ui.notify(curr_config.get_text("notice_start_run"))
        await run.io_bound(run_baah_task_and_bind_log, logArea, json_file_name)

    async def stop_run():
        stop_baah_task(logArea, json_file_name)

    # Server Info Helper
    def set_server_info(servername):
        curr_config.userconfigdict['SERVER_TYPE'] = servername
        curr_config.userconfigdict["PIC_PATH"] = server2pic[servername]
        curr_config.userconfigdict["ACTIVITY_PATH"] = server2activity[servername]
        if curr_config.userconfigdict["LOCK_SERVER_TO_RESPOND_Y"]:
            curr_config.userconfigdict["RESPOND_Y"] = server2respond[servername]

    def render_top_bar():
        with ui.card().classes('w-full h-full p-2 flex flex-row flex-nowrap items-center justify-between shadow-sm gap-2 box-border'):
            # Left Group: Back Button & Title
            with ui.row().classes('items-center gap-2 flex-none'):
                ui.button(icon='arrow_back', on_click=lambda: ui.run_javascript('window.history.back()')).props('flat round dense')
                ui.label(f'{json_file_name}').classes('text-lg font-bold')
            
            # Middle Group: Settings (Server -> ADB -> Emulator Path)
            with ui.row().classes('items-center gap-2 flex-1 justify-start no-wrap overflow-hidden'):
                # 1. Server Selection (Ratio 2)
                server_options = {
                    "JP":curr_config.get_text("config_server_jp"), 
                    "GLOBAL":curr_config.get_text("config_server_global"), 
                    "GLOBAL_EN":curr_config.get_text("config_server_global_en"),
                    "CN":curr_config.get_text("config_server_cn"),
                    "CN_BILI":curr_config.get_text("config_server_cn_b"),
                    "PC_STEAM":"STEAM (Windows)",
                    "PC_STEAM_EN":"STEAM_EN (Windows)",
                    "PC_EXE_JP":f'{curr_config.get_text("config_server_jp")} (PC Windows)'
                }
                
                ui.select(server_options, label=curr_config.get_text("setting_server"), value=curr_config.userconfigdict['SERVER_TYPE'], on_change=lambda e: set_server_info(e.value))\
                    .style('flex: 2; min-width: 0px;').classes('mx-1')

                # ADB & Emulator Visibility Helper
                is_not_pc = lambda v: not _is_PC_app(v)

                # 2. ADB Port/Serial (Ratio 1)
                with ui.element('div').style('flex: 1; min-width: 0px; display: flex; align-items: center;').classes('mx-1').bind_visibility_from(curr_config.userconfigdict, "SERVER_TYPE", is_not_pc):
                    # Port Input
                    ui.number('ADB Port', step=1, precision=0)\
                        .bind_value(curr_config.userconfigdict, 'TARGET_PORT', forward=lambda v: int(v) if v else 5555, backward=lambda v:int(v))\
                        .bind_visibility_from(curr_config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: not v)\
                        .classes('w-full')
                    
                    # Serial Input 
                    ui.input(curr_config.get_text("adb_serial"))\
                        .bind_value(curr_config.userconfigdict, 'ADB_SEIAL_NUMBER')\
                        .bind_visibility_from(curr_config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER", lambda v: v)\
                        .classes('w-full')

                # 3. Serial Checkbox (Ratio 3)
                with ui.element('div').style('flex: 2; min-width: 0px; display: flex; align-items: center; overflow: hidden;').classes('mx-1').bind_visibility_from(curr_config.userconfigdict, "SERVER_TYPE", is_not_pc):
                    ui.checkbox(curr_config.get_text("adb_direct_use_serial"))\
                        .bind_value(curr_config.userconfigdict, 'ADB_DIRECT_USE_SERIAL_NUMBER')\
                        .classes('w-full')
                
                # 4. Emulator Path (Ratio 6)
                with ui.element('div').style('flex: 6; min-width: 0px; display: flex; align-items: center;').classes('mx-1').bind_visibility_from(curr_config.userconfigdict, "SERVER_TYPE", is_not_pc):
                    ui.input(curr_config.get_text("config_emulator_path"))\
                        .bind_value(curr_config.userconfigdict, 'TARGET_EMULATOR_PATH', 
                                   forward=lambda v: v.replace("\\", "/").replace('"','').replace('nx_main/MuMuNxMain.exe','nx_device/12.0/shell/MuMuNxDevice.exe'))\
                        .props('placeholder="模拟器路径"').classes('w-full')

            # Right Group: Action Buttons
            with ui.row().classes('items-center gap-2 flex-none'):
                ui.button('保存配置', icon='save', on_click=save_and_alert).props('flat')
                
                # Signal logic
                msg_obj = RunningBAAHProcess_instance.get_status_obj(configname=json_file_name)
                
                # Container for the run button group
                with ui.row().classes('items-center gap-0'):
                    
                    # RUN BUTTON (GUI)
                    run_btn = ui.button('运行 (GUI)', icon='play_arrow', on_click=run_in_gui) \
                        .classes('blue-button rounded-r-none') \
                        .bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 0)
                    
                    # STOP BUTTON
                    stop_btn = ui.button('停止运行', icon='stop', color='red', on_click=stop_run) \
                        .classes('rounded-r-none') \
                        .bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 1)

                    # DROPDOWN TRIGGER
                    with ui.button(icon='arrow_drop_down').classes('px-1 rounded-l-none border-l border-white/30 blue-button').bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 0):
                        with ui.menu():
                            ui.menu_item('终端运行 (Term)', on_click=run_in_terminal)
                            
                    ui.spinner().bind_visibility_from(msg_obj, "runing_signal", backward=lambda x: x == 0.25)
                
                # Log recovery
                if msg_obj["runing_signal"] == 1:
                    ui.timer(0.5, run_in_gui, once=True)

    # Main Layout
    with ui.element('div').classes('w-full h-screen overflow-hidden p-0 m-0 box-border'):
        
        # 1. Top Bar
        with ui.element('div').classes('w-full h-[60px] z-10 relative'):
            render_top_bar()

        # 2. Main Content Area (1:4:2 Ratio), Fixed height
        # Using flex-basis/grow via style because Tailwind classes flex-1/2/4 might not cover the ratio sum=7 perfectly in default theme
        
        with ui.row().classes('w-full h-[calc(100vh-60px)] p-4 pt-2 gap-4 no-wrap items-stretch'):
            
            # Placeholder for Left and Middle, created first to maintain row order
            left_section = ui.card().classes('h-full p-0 flex flex-col overflow-hidden').style(f'flex: {COLUMN_RATIOS[0]}')
            middle_section = ui.card().classes('h-full p-0 flex flex-col overflow-hidden').style(f'flex: {COLUMN_RATIOS[1]}')
            right_section = ui.column().classes('h-full gap-4 overflow-hidden').style(f'flex: {COLUMN_RATIOS[2]}')

            # Populate Right Section immediately to create logArea
            with right_section:
                # Description Card (Top 1/3 approximately)
                with ui.card().classes('w-full h-1/3 p-0 flex flex-col overflow-hidden'):
                     desc_container = ui.column().classes('w-full h-full p-0') # Placeholder for render

                # Log Card (Bottom 2/3 approximately)
                with ui.card().classes('w-full h-2/3 p-0 flex flex-col overflow-hidden'):
                    ui.label('运行日志').classes('p-2 font-bold border-b border-gray-200 text-xs')
                    with ui.column().classes('w-full flex-grow p-0 overflow-hidden relative'):
                         # Create LogArea here
                         logArea = ui.log(max_lines=1000).classes('w-full h-full font-mono text-xs p-2 overflow-auto absolute inset-0')

            # Now that logArea exists, get the config list
            config_choose_list = get_config_list(curr_config, logArea, obj_parsed_dict_of_config)
            current_panel = config_choose_list[0] if config_choose_list else None
            
            # Populate Left Section
            with left_section:
                 # Tab Change Handler
                 def on_tab_change(e):
                    nonlocal current_tab_type
                    # Convert integer value back to Enum for filtering
                    current_tab_type = ConfigPanelType(e.value)
                    render_task_list.refresh()

                 with ui.tabs().classes('w-full border-b border-gray-200').on_value_change(on_tab_change) as tabs:
                    for tabkey in panel_types_2_str.keys():
                        this_tab = ui.tab(name=tabkey.value, label=panel_types_2_str.get(tabkey)).classes('flex-1')
                 
                 # Set default value
                 tabs.set_value(ConfigPanelType.BAAH_Bsic_Settings.value)

                 with ui.column().classes('w-full flex-grow overflow-y-auto p-0'):
                     render_task_list()

            # Populate Middle Section
            with middle_section:
                 render_config_area()

            # Populate Description in previously created container
            with desc_container:
                 render_description()
