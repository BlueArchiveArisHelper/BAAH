import os
import os
import win32com.client

# 打印当前程序运行路径
print("os.getcwd: ", os.getcwd())
_running_path = os.getcwd().replace("_internal", "")
print("running path: ", _running_path)

def create_shortcut_file(config_name, link_name, run_path, save_path):
    """
    创建启动BAAH的快捷方式保存到指定路径

    :param config_name: 配置文件名
    :param link_name: 快捷方式文件名
    :param run_path: BAAH.exe所在文件夹路径
    :param save_path: 快捷方式保存文件夹路径
    """
    try:
        # 创建 Shell 对象
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(os.path.join(save_path, link_name))

        # 设置快捷方式的关键属性
        shortcut.TargetPath = os.path.join(run_path, "BAAH.exe")
        shortcut.WorkingDirectory = run_path  # 设置工作目录（启动位置）
        shortcut.IconLocation = os.path.join(run_path, "DATA/icons/aris.ico")  # 设置图标
        # shortcut.Arguments = "--start-maximized"  # 可以设置启动参数（可选）

        # 保存快捷方式
        shortcut.save()
        return True
    except Exception as e:
        return False

def send_quick_call_to_desktop(config_name):
    # 获取桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    return create_shortcut_file(config_name, "BAAH "+config_name.replace(".json", ".lnk"), _running_path, desktop_path)