# 将当前脚本所在目录添加到模块搜索路径
import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)
# config logging before all imports
from modules.utils.log_utils import logging
from main import run_baah_script


def main():
    # Use freeze_support to avoid running GUI again: https://blog.csdn.net/fly_leopard/article/details/121610641
    import multiprocessing
    multiprocessing.freeze_support()
    if not multiprocessing.get_start_method(allow_none=True):
        from gui.components.exec_arg_parse import parse_args
        from modules.configs.MyConfig import MyConfigger
        from nicegui import ui, app
        
        print("GUI is running...")
        args = parse_args()
        if (args.config is not None and args.config.endswith(".json")):
            run_baah_script(args.config)
        else:
            ui.run(title=f"BAAH{MyConfigger.NOWVERSION}", language="zh-cn", reload=False, host=args.host, port=args.port, show=args.show, storage_secret="32737")

if __name__ in {"__main__", "__mp_main__"}:
    main()
