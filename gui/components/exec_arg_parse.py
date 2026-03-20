import argparse
import os
from nicegui import native, app, ui

g_token: str = ""

def parse_args():
    parser = argparse.ArgumentParser()
    # 添加位置参数（可选）：用于接收配置文件路径
    parser.add_argument(
        "config", 
        nargs="?",  # "?"表示该参数可选（提供0次或1次）
        help="config file name",
        default=None  # 未提供时为None
    )
    parser.add_argument(
        "--host", help="host address", default=os.environ.get("HOST", "127.0.0.1")
    )
    parser.add_argument(
        "--port",
        help="host port",
        default=os.environ.get("PORT", native.find_open_port()),
    )
    parser.add_argument(
        "--token", help="password", default=os.environ.get("TOKEN", None)
    )
    parser.add_argument(
        "--no-show", action="store_false", dest="show", help="disable open browser"
    )
    args = parser.parse_args()
    global g_token
    g_token = args.token
    return args


def get_token() -> str:
    return g_token


def check_token_dialog(refresh_page):
    if g_token is not None and len(g_token) != 0 and g_token != app.storage.user.get("token"):
        with ui.card().classes('absolute-center'):
            ui.input('Token', password=True, password_toggle_button=True,
                     on_change=lambda e: [app.storage.user.update({"token": e.value}),
                                          refresh_page.refresh() if e.value == g_token else None])
        return False
    else:
        return True
