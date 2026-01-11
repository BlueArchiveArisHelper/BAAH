import sys
import os

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 生成列表
with open(os.path.join(SCRIPT_DIR, 'requirements.txt'), 'r') as file:
    lines = file.readlines()
    core_list = lines[lines.index('###CORE###\n') + 1:lines.index('###CORE_END###\n')]
    build_list = lines[lines.index('###BUILD###\n') + 1:lines.index('###BUILD_END###\n')]

NOT_SUPPORT_PYTHON_VERSION = False
IS_DOCKER = False

if sys.platform == 'linux':
    if os.path.exists("/.dockerenv"):
        IS_DOCKER = True

if sys.version_info[:2] != (3, 10):
    NOT_SUPPORT_PYTHON_VERSION = True

if sys.implementation.name != 'cpython':
    raise Exception("Only CPython is supported.")

if __name__ == '__main__':
    if sys.version_info[:2] == (3, 12):
        for core_list_item in core_list:
            if "onnxruntime" in core_list_item:
                del core_list[core_list.index(core_list_item)]
                core_list.append("onnxruntime==1.17.0\n")
        print("已针对Python 3.12生成依赖列表，注意，Python 3.12不受官方支持。")
        print("The dependency list has been generated for Python 3.12, note that Python 3.12 is not officially supported.")
    elif NOT_SUPPORT_PYTHON_VERSION is True:
        print("警告: 你正在使用不受支持的Python版本，某些依赖可能无法正确安装。")
        print("Warning: You are using an unsupported Python version, some dependencies may not install correctly.")
                
    if IS_DOCKER:
        print("你现在正在Docker容器中运行，请确保你已安装libgl1或相关依赖以支持onnxruntime")
        print("You are currently running in a Docker container. Please ensure you have installed libgl1 or related dependencies to support onnxruntime.")
    if "--core" in sys.argv:
        print("生成核心依赖列表 requirforyou.txt for core dependencies.")
        with open(os.path.join(SCRIPT_DIR, 'requirforyou.txt'), 'w') as f:
            f.writelines(core_list)
    elif "--build" in sys.argv:
        print("生成构建依赖列表 requirforyou.txt for build dependencies.")
        with open(os.path.join(SCRIPT_DIR, 'requirforyou.txt'), 'w') as f:
            f.writelines(build_list)
    else:
        print("请使用 --core 或 --build 生成依赖列表。")
