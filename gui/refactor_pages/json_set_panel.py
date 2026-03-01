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
from ..pages.Setting_task_order import set_task_order # 此方法内有个导入myAllTask，可能导致下述异常
from ..pages.Setting_timetable import set_timetable
from ..pages.Setting_wanted import set_wanted
from ..pages.Setting_notification import set_notification
from ..pages.Setting_vpn import set_vpn
from ..pages.Setting_Assault import set_assault
from ..pages.Setting_BuyAP import set_buyAP
from ..pages.Setting_UserTask import set_usertask
from ..pages.Setting_explore import set_explore
from ..pages.Setting_Oneclick_Raid import set_oneclick_raid
from modules.AllTask.myAllTask import task_instances_map # 这里导入myAllTask可能会导致其内my_AllTask单例值异常，目前通过在run()里使用前再读取config的任务列表解决此bug
from modules.configs.MyConfig import MyConfigger
from ..define import gui_shared_config, injectJSforTabs
from define_actions.basic_objects import FlowActionGroup

from nicegui import ui, app, run
from typing import Callable
import os
import time


# ---------- 自定义组件封装 ----------

def titled_card(title: str, content_func, classes: str = ''):
    """
    封装的卡片组件
    :param title: 卡片标题
    :param content_func: 渲染卡片内容的 lambda 或函数
    :param classes: 额外的 CSS 类（用于控制高度、宽度等）
    """
    # 默认加上 p-6 和 box-border 保持间距一致
    with ui.card().classes(f'p-6 box-border {classes}'):
        if title:
            ui.label(title).classes('section-title text-lg font-bold mb-6')
        # 执行传入的内容函数
        content_func()

# ---------- 页面主函数 ----------
@ui.page('/panel/{json_file_name}')
def show_json_panel():
    # 设置页面整体样式
    ui.add_head_html('''
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background-color: #f5f5f5; 
                margin: 0;
                padding: 0;
                overflow: hidden; 
            }
            .section-title { 
                font-size: 16px; 
                font-weight: 600; 
                margin-bottom: 10px; 
                color: #333; 
            }
            .task-item { 
                padding: 8px 12px; 
                border-bottom: 1px solid #eee; 
            }
            .log-entry { 
                font-family: 'Consolas', monospace; 
                font-size: 13px; 
                padding: 4px 0; 
            }
            .blue-button { 
                background: #1976d2 !important; 
                color: white !important; 
            }
            .config-row {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            .config-label {
                width: 120px;
                font-weight: 500;
                color: #555;
            }
            .config-input {
                flex: 1;
            }
        </style>
    ''')

    # 任务开始回调
    def start_tasks():
        ui.notify('任务开始执行...', type='info')

    # 主容器
    with ui.column().classes('w-full h-screen p-4 box-border'):
        
        # ========== 上面 15% 区域 (直接封装) ==========
        def top_settings_content():
            with ui.row().classes('w-full h-full items-center justify-between p-2 gap-8 box-border'):
                with ui.row().classes('flex-1 items-center'):
                    ui.label('游戏区服').classes('mr-4')
                    ui.select(['官服', 'B服'], value='官服').classes('flex-1')
                
                with ui.row().classes('flex-1 items-center'):
                    ui.label('模拟器路径').classes('mr-4')
                    with ui.row().classes('flex-1 items-center'):
                        ui.input(placeholder='请输入模拟器安装路径').classes('flex-1')
                        ui.button(icon='folder').props('flat').classes('ml-2')
                
                with ui.row().classes('flex-1 items-center'):
                    ui.label('ADB连接').classes('mr-4')
                    ui.input(placeholder='127.0.0.1:5555', value='127.0.0.1:5555').classes('flex-1')

        titled_card(title='', content_func=top_settings_content, classes='w-full h-[15%] mb-4')

        # ========== 下面 85% 区域 ==========
        with ui.row().classes('w-full h-[85%] gap-4 box-border no-wrap'):
            
            # 第一列：任务列表
            def task_list_content():
                tasks = [
                    {'name': '启动游戏', 'checked': True},
                    {'name': '活动刷取', 'checked': True},
                    {'name': '自动战斗', 'checked': True},
                    {'name': '领取奖励', 'checked': True},
                    {'name': '切换账号', 'checked': False},
                    {'name': '关闭游戏', 'checked': False},
                ]
                with ui.column().classes('w-full flex-grow'):
                    for task in tasks:
                        with ui.row().classes('task-item w-full items-center hover:bg-gray-50 rounded'):
                            ui.checkbox(value=task['checked'])
                            ui.label(task['name']).classes('ml-3 flex-grow')
                
                with ui.row().classes('justify-center mt-auto pt-4'):
                    ui.button('开始任务', icon='play_arrow', on_click=start_tasks) \
                        .classes('blue-button py-3 px-8 text-lg font-medium')

            titled_card('任务列表', task_list_content, classes='h-full flex-1')

            # 第二列：任务配置
            def task_config_content():
                with ui.column().classes('w-full'):
                    configs = [
                        ('控制器类型', lambda: ui.select(['模拟器', '真机'], value='模拟器')),
                        ('当前设备', lambda: ui.select(['MuMu安卓设备', '雷电模拟器', '夜神模拟器'], value='MuMu安卓设备')),
                        ('优先级', lambda: ui.select(['高', '中', '低'], value='中')),
                    ]
                    for label, widget in configs:
                        with ui.row().classes('config-row w-full'):
                            ui.label(label).classes('config-label')
                            widget().classes('config-input')
                    
                    with ui.row().classes('config-row w-full'):
                        ui.label('执行次数').classes('config-label')
                        ui.number(value=1, min=1).classes('config-input')
                    
                    with ui.row().classes('config-row w-full'):
                        ui.label('超时时间').classes('config-label')
                        ui.number(value=30).classes('flex-1')
                        ui.label('分钟').classes('ml-2')
                
                with ui.row().classes('justify-end mt-auto pt-4'):
                    ui.button('保存配置', icon='save').classes('blue-button')

            titled_card('任务配置', task_config_content, classes='h-full flex-1')

            # 第三列：说明 + 日志
            with ui.column().classes('h-full flex-1 gap-4 box-border'):
                
                # 任务说明
                def info_content():
                    with ui.column().classes('h-full w-full overflow-y-auto text-gray-700 text-sm'):
                        ui.label('功能说明:').classes('font-bold')
                        ui.markdown('1. 支持多账号自动切换\n2. 建议分辨率 1280*720\n3. 官服/B服通用')
                        ui.label('注意事项:').classes('font-bold mt-2')
                        ui.label('• 运行期间请勿操作模拟器').classes('text-red-600')

                titled_card('任务说明', info_content, classes='h-[55%] w-full')

                # 运行日志
                def log_content():
                    with ui.column().classes('h-full w-full overflow-hidden'):
                        with ui.column().classes('flex-grow w-full overflow-y-auto bg-gray-50 p-2 rounded'):
                            log_entries = ['11:13:42 正在连接...', '11:13:43 连接成功', '11:13:45 执行任务: 启动']
                            for entry in log_entries:
                                ui.label(entry).classes('log-entry border-b border-gray-100')
                        
                        with ui.row().classes('justify-end mt-2 gap-2'):
                            ui.button(icon='delete').props('flat dense')
                            ui.button('导出', icon='download').props('dense').classes('blue-button px-2')

                titled_card('运行日志', log_content, classes='h-[45%] w-full')