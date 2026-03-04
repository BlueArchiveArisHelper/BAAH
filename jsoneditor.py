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
        from gui.refactor_pages import home_page, show_json_panel # 载入路由
        from gui.components.exec_arg_parse import parse_args
        from modules.configs.MyConfig import MyConfigger
        from nicegui import ui, app
        
        # 自定义界面主题
        # 检查文件
        if not os.path.exists(os.path.join(current_dir, "DATA", "custom", "style.css")):
            with open(os.path.join(current_dir, "DATA", "custom", "style.css"), "w", encoding="utf-8") as f:
                f.write("""
                        /* BAAH自定义样式文件 */
                        /* 此文件会直接注入到BAAH所有页面的<head><style></style></head>中，可以修改页面样式 */
                        /* 如果玩坏了，删掉这个文件就行，BAAH会重新生成并恢复原来样式 */
                        """)
        if not os.path.exists(os.path.join(current_dir, "DATA", "custom", "head.html")):
            with open(os.path.join(current_dir, "DATA", "custom", "head.html"), "w", encoding="utf-8") as f:
                f.write("""
                        <!-- BAAH自定义head文件 -->
                        <!-- 此文件会直接注入到BAAH所有页面的<head></head>中，可以修改页面头部内容 -->
                        <!-- 如果你要自己编辑样式，请编辑style.css -->
                        <!-- 如果玩坏了，删掉这个文件就行，BAAH会重新生成并恢复原来头部内容 -->
                        """)
        if not os.path.exists(os.path.join(current_dir, "DATA", "custom", "body.html")):
            with open(os.path.join(current_dir, "DATA", "custom", "body.html"), "w", encoding="utf-8") as f:
                f.write("""
                        <!-- BAAH自定义body文件 -->
                        <!-- 此文件会直接注入到BAAH所有页面的<body></body>中，可以注入或引入脚本 -->
                        <!-- 建议添加 async 或 defer 属性来优化性能 -->
                        <!-- 如果玩坏了，删掉这个文件就行，BAAH会重新生成并恢复原来头部内容 -->
                        """)
        if not os.path.exists(os.path.join(current_dir, "DATA", "custom", "static")):
            os.makedirs(os.path.join(current_dir, "DATA", "custom", "static"))
            with open(os.path.join(current_dir, "DATA", "custom", "static", "README.md"), "w", encoding="utf-8") as f:
                f.write("""
                        # 目录说明

                        此目录为自定义静态文件目录，用于存放自定义的静态文件，如图片、CSS、JavaScript等。

                        若要修改CSS,建议直接修改`style.css`或将css文件放入此目录下，在`head.html`中引入。

                        ## 用法

                        目录映射关系：`DATA/custom/static/` -> `/custom/static/`

                        如果你想添加背景图，将`background.jpg`放入此目录，然后在`style.css`中调用，如：

                        ``` css
                        body {
                            background-image: url("/custom/static/background.jpg");
                        }
                        ```
                        """)
        
        # 注入自定义样式,head, body
        with open(os.path.join(current_dir, "DATA", "custom", "style.css"), "r", encoding="utf-8") as f:
            ui.add_css(f.read(),shared=True)
        with open(os.path.join(current_dir, "DATA", "custom", "head.html"), "r", encoding="utf-8") as f:
            ui.add_head_html(f.read(),shared=True)
        with open(os.path.join(current_dir, "DATA", "custom", "body.html"), "r", encoding="utf-8") as f:
            ui.add_body_html(f.read(),shared=True)
        # 映射静态文件 DATA/custom/static --> /custom/static
        app.add_static_files("/custom/static", os.path.join(current_dir, "DATA", "custom", "static"))
        
        print("GUI is running...")
        args = parse_args()
        if (args.config is not None and args.config.endswith(".json")):
            run_baah_script(args.config)
        else:
            ui.run(title=f"BAAH{MyConfigger.NOWVERSION}", language="zh-cn", reload=False, host=args.host, port=args.port, show=args.show, storage_secret="32737")

if __name__ in {"__main__", "__mp_main__"}:
    # 检查是否有BAAH_GUI.exe 文件，删除
    # 这边current_dir要去掉_internal
    print(f"Detect in {current_dir}")
    exe_path = os.path.join(current_dir.replace("_internal", ""), "BAAH_GUI.exe")
    print(f"Detect GUI.exe : {os.path.exists(exe_path)}")
    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
            logging.info("Removed existing BAAH_GUI.exe file.")
        except Exception as e:
            logging.error(f"Failed to remove BAAH_GUI.exe: {e}")

    main()
