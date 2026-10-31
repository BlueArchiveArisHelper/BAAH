from enum import Enum
from ..components.background_settings import apply_background
# 公共视觉组件仅负责容器与样式，保留原有配置和运行逻辑。
from ..components.modern_ui import (
    apply_theme, page_shell, surface, navigation_item, description_panel, log_panel,
)

from ..components.exec_arg_parse import get_token
from ..components.manage_baah_in_gui import run_baah_task_and_bind_log, stop_baah_task
from ..components.running_task_pool import RunningBAAHProcess_instance
from ..components.web_dark_mode import apply_dark_mode, change_dark_mode
from ..components.mumu_emulator_path_recognize import smart_replace_main2device
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
from ..pages.Setting_Grand_Assault import set_grand_assault
from ..pages.Setting_BuyAP import set_buyAP
from ..pages.Setting_UserTask import set_usertask
from ..pages.Setting_explore import set_explore
from ..pages.Setting_Oneclick_Raid import set_oneclick_raid
from ..pages.Setting_quick_runtask import set_quick_runtask
from ..pages.Setting_CrashReportsManager import Set_Crash_Report_Manager
from modules.AllTask.myAllTask import task_instances_map
from modules.configs.MyConfig import MyConfigger
from modules.utils import _is_PC_app, _is_STEAM_app
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


# 分类名称与图标共同维护，导航只读取分类元数据。
panel_types_2_str = {
    ConfigPanelType.BAAH_Bsic_Settings: {"name": "BAAH", "icon": "settings"},
    ConfigPanelType.Daily_Task_Settings: {
        "name": gui_shared_config.get_text("setting_daily"),
        "icon": "event_note",
    },
    ConfigPanelType.Quick_Task_Settings: {
        "name": gui_shared_config.get_text("config_quick_call_task"),
        "icon": "build",
    },
}


class ConfigPanel:
    """
    集中定义子页面的名称、图标、分类与渲染入口。

    Parameters
    ==========
    nameID: str
        子页面标题的i18n的key 或 标题名
    func:
        子页面渲染函数
    desc:
        子页面说明渲染函数 (lambda)
    i18n_config:
        传入时通过nameID找到对应i18n名字作为name，为None时name=nameID
    panel_types
        该配置项所属的类型列表，决定在不同的 Tab 栏目下是否显示
    icon: str
        导航图标名，与页面一同注册；省略时使用 settings
    enterCallback: lambda
        进入此页面时需要执行的回调
    quitCallback: lambda
        退出此页面时需要执行的回调
    """

    def __init__(
        self,
        nameID: str,
        func: Callable[[], None],
        desc: Callable[[], None] = None,
        i18n_config=None,
        panel_types=[ConfigPanelType.BAAH_Bsic_Settings],
        *,
        icon: str = 'settings',
        enterCallback = None,
        quitCallback = None
    ):
        self.name = i18n_config.get_text(nameID) if i18n_config else nameID
        self.func = func
        # 未提供说明时，沿用页面名称作为默认说明。
        self.desc = desc if desc else lambda: ui.label(f"{self.name}")
        self.nameID = nameID
        self.panel_types = panel_types
        self.icon = icon
        self.enterCallback = enterCallback
        self.quitCallback = quitCallback


def parse_obj_in_config(inconfig, obj_dict, backward=False):
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
        "OBJ_ACTIONS_VPN_START": lambda x: x.to_json_dict(),
        "OBJ_ACTIONS_VPN_SHUT": lambda x: x.to_json_dict(),
        "OBJ_USER_DEFINE_TASK": lambda x: x.to_json_dict(),
        "OBJ_FLOW_WHEN_LOGIN": lambda x: x.to_json_dict(),
    }
    if not backward:  # json转对象，存obj_dict
        for key, clsa in parse_mapping.items():
            if key in inconfig.userconfigdict:
                obj_dict[key] = clsa(inconfig.userconfigdict[key])
    else:
        for key, clsa in reverse_mapping.items():  # 对象转json，存userconfigdict
            if key in obj_dict:
                inconfig.userconfigdict[key] = clsa(obj_dict[key])


def get_config_list(lst_config: MyConfigger, logArea, parsed_obj_dict) -> list:
    return [
        ConfigPanel(
            "BAAH",
            lambda: set_BAAH(lst_config, gui_shared_config),
            icon='info_outline',
            i18n_config=None,
            panel_types=[ConfigPanelType.BAAH_Bsic_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("BAAH_desc")),
        ),
        # ConfigPanel("setting_server", lambda: set_server(lst_config), i18n_config=lst_config, panel_types = [ConfigPanelType.BAAH_Bsic_Settings]),
        ConfigPanel(
            "setting_emulator",
            lambda: set_emulator(lst_config),
            icon='devices',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.BAAH_Bsic_Settings],
        ),
        ConfigPanel(
            "setting_other",
            lambda: set_other(lst_config, gui_shared_config),
            icon='tune',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.BAAH_Bsic_Settings],
        ),
        ConfigPanel(
            "setting_crash_report_manager",
            lambda: Set_Crash_Report_Manager(lst_config),
            icon='bug_report',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.BAAH_Bsic_Settings],
        ),
        ConfigPanel(
            "setting_task_order",
            lambda: set_task_order(
                lst_config, task_instances_map.task_config_name_2_i18n_name, logArea
            ),
            icon='format_list_numbered',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "setting_vpn",
            lambda: set_vpn(lst_config, parsed_obj_dict),
            icon='vpn_lock',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "setting_notification",
            lambda: set_notification(lst_config, gui_shared_config),
            icon='notifications_none',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_login_game",
            lambda: set_login(lst_config, parsed_obj_dict),
            icon='exit_to_app',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_cafe",
            lambda: set_cafe(lst_config),
            icon='local_cafe',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_timetable",
            lambda: set_timetable(lst_config),
            icon='date_range',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_craft",
            lambda: set_craft(lst_config),
            icon='build',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_shop",
            lambda: set_shop(lst_config),
            icon='shopping_cart',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_buy_ap",
            lambda: set_buyAP(lst_config),
            icon='flash_on',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_wanted",
            lambda: set_wanted(lst_config),
            icon='my_location',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_special",
            lambda: set_special(lst_config),
            icon='assignment',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_exchange",
            lambda: set_exchange(lst_config),
            icon='school',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_exam",
            lambda: set_exam(lst_config),
            icon='assignment_turned_in',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_event",
            lambda: set_event(lst_config),
            icon='event',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_assault",
            lambda: set_assault(lst_config),
            icon='security',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_grand_assault",
            lambda: set_grand_assault(lst_config),
            icon='group_work',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_oneclick_raid",
            lambda: set_oneclick_raid(lst_config),
            icon='playlist_play',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "task_hard",
            lambda: set_hard(lst_config, gui_shared_config),
            icon='layers',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_normal",
            lambda: set_normal(lst_config),
            icon='view_module',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
            desc=lambda: ui.markdown(gui_shared_config.get_text("config_desc_times")),
        ),
        ConfigPanel(
            "task_user_def_task",
            lambda: set_usertask(lst_config, parsed_obj_dict),
            icon='account_tree',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Daily_Task_Settings],
        ),
        ConfigPanel(
            "config_quick_call_task",
            lambda: set_quick_runtask(
                lst_config, task_instances_map.task_config_name_2_i18n_name, logArea
            ),
            icon='play_circle_outline',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Quick_Task_Settings],
            desc=lambda: ui.markdown(
                gui_shared_config.get_text("config_desc_quick_call_task")
            ),
        ),
        ConfigPanel(
            "setting_explore",
            lambda: set_explore(
                lst_config, task_instances_map.task_config_name_2_i18n_name, logArea
            ),
            icon='explore',
            i18n_config=lst_config,
            panel_types=[ConfigPanelType.Quick_Task_Settings],
        ),
    ]


# ---------- 页面主函数 ----------
@ui.page("/panel/{json_file_name}")
async def show_json_panel(json_file_name: str):
    # 直达配置页也需在首次等待前注册样式，确保“跟随系统”模式下布局正常。
    apply_theme()
    apply_background(gui_shared_config)
    await apply_dark_mode(gui_shared_config)
    # 0. Setup and Parse same as old file
    obj_parsed_dict_of_config = {}
    if get_token() is not None and get_token() != app.storage.user.get("token"):
        return
    curr_config: MyConfigger = MyConfigger()
    curr_config.parse_user_config(json_file_name)
    parse_obj_in_config(curr_config, obj_parsed_dict_of_config)

    # Placeholders for controls that need to be accessed
    logArea = None

    # State for selected panel
    current_panel = None
    config_choose_list = []
    current_tab_type = ConfigPanelType.BAAH_Bsic_Settings

    # Refreshable areas
    @ui.refreshable
    def render_task_list():
        with ui.column().classes("w-full gap-0"):
            # Filter config list based on current tab
            filtered_list = [
                p for p in config_choose_list if current_tab_type in p.panel_types
            ]

            for panel in filtered_list:
                # 导航统一封装为可键盘操作的按钮，不改变页面选择回调。
                navigation_item(panel.name, panel == current_panel,
                                lambda _, p=panel: select_panel(p),
                                icon=panel.icon)

    @ui.refreshable
    def render_config_area():
        if current_panel:
            with ui.column().classes('baah-form'):
                ui.label(current_panel.name).classes('baah-form-title')
                render_description()
                # 所有已注册设置页共用表单容器，动态表单仍由原函数生成。
                with ui.column().classes('baah-form-body'):
                    if current_panel.enterCallback is not None:
                        current_panel.enterCallback()
                    current_panel.func()

    @ui.refreshable
    def render_description():
        if current_panel:
            with description_panel(gui_shared_config.get_text('text_description')):
                current_panel.desc()

    def select_panel(panel):
        nonlocal current_panel
        if current_panel.quitCallback is not None:
            current_panel.quitCallback()
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
        curr_config.userconfigdict["SERVER_TYPE"] = servername
        curr_config.userconfigdict["PIC_PATH"] = server2pic[servername]
        curr_config.userconfigdict["ACTIVITY_PATH"] = server2activity[servername]
        if curr_config.userconfigdict["LOCK_SERVER_TO_RESPOND_Y"]:
            curr_config.userconfigdict["RESPOND_Y"] = server2respond[servername]

    def render_top_bar():
        # 顶栏拆为操作与连接设置两层，避免路径和按钮相互挤压。
        with surface('baah-header'):
            with ui.row().classes('baah-title-row'):
                with ui.row().classes("baah-brand"):
                    ui.button(
                        icon="arrow_back",
                        on_click=lambda: ui.run_javascript("window.history.back()"),
                    ).props("flat round dense")
                    ui.label(f"{json_file_name}").classes("baah-brand-name")

                with ui.row().classes("baah-operation-bar"):
                    ui.button(
                        gui_shared_config.get_text("button_save"),
                        icon="save",
                        on_click=save_and_alert,
                    ).props("flat")

                    # Signal logic
                    msg_obj = RunningBAAHProcess_instance.get_status_obj(
                        configname=json_file_name
                    )

                    # Container for the run button group
                    with ui.row().classes("items-center gap-0"):

                        # RUN BUTTON (GUI)
                        run_btn = (
                            ui.button(
                                gui_shared_config.get_text("button_save_and_run_gui"),
                                icon="play_arrow",
                                on_click=run_in_gui,
                            )
                            .classes("blue-button rounded-r-none")
                            .bind_visibility_from(
                                msg_obj, "runing_signal", backward=lambda x: x == 0
                            )
                        )

                        # STOP BUTTON
                        stop_btn = (
                            ui.button(
                                gui_shared_config.get_text("notice_finish_run"),
                                icon="stop",
                                color="red",
                                on_click=stop_run,
                            )
                            .classes("rounded-r-none")
                            .bind_visibility_from(
                                msg_obj, "runing_signal", backward=lambda x: x == 1
                            )
                        )

                        # DROPDOWN TRIGGER
                        with ui.button(icon="arrow_drop_down").classes(
                            "px-1 rounded-l-none border-l border-white/30 blue-button"
                        ).bind_visibility_from(
                            msg_obj, "runing_signal", backward=lambda x: x == 0
                        ):
                            with ui.menu().classes("min-w-60"):
                                ui.menu_item(
                                    gui_shared_config.get_text(
                                        "button_save_and_run_terminal"
                                    ),
                                    on_click=run_in_terminal,
                                )

                        ui.spinner().bind_visibility_from(
                            msg_obj, "runing_signal", backward=lambda x: x == 0.25
                        )

                    # Log recovery
                    if msg_obj["runing_signal"] == 1:
                        ui.timer(0.5, run_in_gui, once=True)

            with ui.row().classes(
                "baah-connection"
            ):
                # 1. Server Selection (Ratio 2)
                server_options = {
                    "JP": curr_config.get_text("config_server_jp"),
                    "GLOBAL": curr_config.get_text("config_server_global"),
                    "GLOBAL_EN": curr_config.get_text("config_server_global_en"),
                    "CN": curr_config.get_text("config_server_cn"),
                    "CN_BILI": curr_config.get_text("config_server_cn_b"),
                    "PC_STEAM": "STEAM (Windows)",
                    "PC_STEAM_EN": "STEAM_EN (Windows)",
                    "PC_EXE_JP": f'{curr_config.get_text("config_server_jp")} (PC Windows)',
                }

                ui.select(
                    server_options,
                    label=curr_config.get_text("setting_server"),
                    value=curr_config.userconfigdict["SERVER_TYPE"],
                    on_change=lambda e: set_server_info(e.value),
                ).classes("baah-server")

                # ADB & Emulator Visibility Helper
                is_not_pc = lambda v: not _is_PC_app(v)

                # 2. ADB Port/Serial (Ratio 1)
                with ui.row().classes("baah-address").bind_visibility_from(
                    curr_config.userconfigdict, "SERVER_TYPE", is_not_pc
                ):
                    # IP Input
                    ui.input(curr_config.get_text("config_ip_root")).bind_value(
                        curr_config.userconfigdict,
                        "TARGET_IP_PATH",
                        forward=lambda v: v.replace("\\", "/"),
                    ).bind_visibility_from(
                        curr_config.userconfigdict,
                        "ADB_DIRECT_USE_SERIAL_NUMBER",
                        lambda v: not v,
                    ).classes(
                        "w-full"
                    )

                    # Port Input
                    ui.number(curr_config.get_text("config_emulator_port"), step=1, precision=0).bind_value(
                        curr_config.userconfigdict,
                        "TARGET_PORT",
                        forward=lambda v: int(v) if v else 5555,
                        backward=lambda v: int(v),
                    ).bind_visibility_from(
                        curr_config.userconfigdict,
                        "ADB_DIRECT_USE_SERIAL_NUMBER",
                        lambda v: not v,
                    ).classes(
                        "w-full"
                    )

                    # Serial Input
                    ui.input(curr_config.get_text("adb_serial")).bind_value(
                        curr_config.userconfigdict, "ADB_SEIAL_NUMBER"
                    ).bind_visibility_from(
                        curr_config.userconfigdict,
                        "ADB_DIRECT_USE_SERIAL_NUMBER",
                        lambda v: v,
                    ).classes(
                        "w-full"
                    )

                # 3. Serial Checkbox (Ratio 3)
                with ui.element("div").classes("baah-serial").bind_visibility_from(
                    curr_config.userconfigdict, "SERVER_TYPE", is_not_pc
                ):
                    ui.checkbox(
                        curr_config.get_text("adb_direct_use_serial")
                    ).bind_value(
                        curr_config.userconfigdict, "ADB_DIRECT_USE_SERIAL_NUMBER"
                    ).classes(
                        "w-full"
                    )

                with ui.element("div").classes("baah-path").bind_visibility_from(
                    curr_config.userconfigdict,
                    "SERVER_TYPE",
                    lambda v: not _is_STEAM_app(v),
                ):
                    ui.input(curr_config.get_text("config_emulator_path")).bind_value(
                        curr_config.userconfigdict,
                        "TARGET_EMULATOR_PATH",
                        forward=smart_replace_main2device,
                    ).props('placeholder="模拟器路径"').classes("w-full")


    # 编辑器使用正常 flex 布局，日志展开时缩小表单区域而不覆盖控件。
    with page_shell():
        render_top_bar()
        with ui.row().classes('baah-workspace') as workspace:
            left_section = surface('baah-nav')
            middle_section = surface('baah-main')

        # 日志实例在注册设置页前创建，折叠和页面刷新均不会替换它。
        logArea = log_panel(gui_shared_config.get_text('text_log'))
        config_choose_list = get_config_list(curr_config, logArea, obj_parsed_dict_of_config)
        current_panel = config_choose_list[0] if config_choose_list else None

        with left_section:
            def on_tab_change(e):
                nonlocal current_tab_type
                current_tab_type = ConfigPanelType(e.value)
                render_task_list.refresh()

            # 一级页签使用横向图文排列，名称与图标来自同一分类定义。
            with ui.tabs().props('inline-label').on_value_change(on_tab_change) as tabs:
                for tabkey, metadata in panel_types_2_str.items():
                    ui.tab(name=tabkey.value, label=metadata['name'],
                           icon=metadata['icon'])
            tabs.set_value(ConfigPanelType.BAAH_Bsic_Settings.value)
            with ui.column().classes('baah-nav-scroll'):
                render_task_list()

        with middle_section:
            # 小窗口专用导航开关只切换展示类，不接触配置参数。
            ui.button(icon='menu', on_click=lambda: workspace.classes(
                toggle='baah-nav-collapsed')).props('flat').classes('baah-nav-toggle').tooltip(
                    gui_shared_config.get_text('setting_daily'))
            render_config_area()
