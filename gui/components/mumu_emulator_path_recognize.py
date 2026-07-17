import os
import subprocess
import json

def _find_param_value(emulator_path, param_name):
    if param_name in emulator_path:
        parts = emulator_path.split(param_name)
        if len(parts) > 1:
            return parts[1].strip().split()[0].strip('"').replace('=', '')
    return None

def smart_replace_main2device(emulator_path):
    """将mumu多开器路径根据 --engine_series 参数选择替换为对应的路径模拟器"""
    print(f"Original emulator path: {emulator_path}")
    emulator_path = emulator_path.replace("\\", "/").replace('"', "").replace(" --from-shortcut","")
    replaced_off_str = "nx_main/MuMuNxMain.exe"
    final_emulator_path = emulator_path
    if replaced_off_str not in emulator_path:
        return final_emulator_path
    nx_main_dir = os.path.join(emulator_path.split(replaced_off_str, 1)[0], "nx_main")
    nx_device_dir = os.path.join(emulator_path.split(replaced_off_str, 1)[0], "nx_device")
    # # Mumu 多开器替换逻辑
    mumu_version = "15.0" # 默认15
    # 1. 有 --engine_series 参数，则直接替换为对应的路径模拟器
    if "--engine_series" in emulator_path and _find_param_value(emulator_path, "--engine_series"):
        mumu_version = _find_param_value(emulator_path, "--engine_series")
        print(f"Found --engine_series parameter: {mumu_version}")
        replaced_on_str = "nx_device/{}/shell/MuMuNxDevice.exe".format(mumu_version)
        final_emulator_path = emulator_path.replace(replaced_off_str, replaced_on_str).replace(f" --engine_series={mumu_version}", "")
        return final_emulator_path
    else:
        # 2. 根据 MuMuManager.exe info -v 0 查找
        vindex = _find_param_value(emulator_path, "-v")
        print(f"Found -v parameter: {vindex}")
        vindex = vindex if vindex else "0"  # 默认使用 -v 0
        mumumanager_path = os.path.join(nx_main_dir, "MuMuManager.exe")
        # 通过 MuMuManager.exe info -v 0 查找对应的 --engine_series 参数值
        try:
            result = subprocess.run([mumumanager_path, "info", "-v", vindex], capture_output=True, text=True, encoding="utf-8")
            if result.returncode == 0:
                output = result.stdout
                infodict = json.loads(output)
                if "android_version" in infodict:
                    mumu_version = infodict["android_version"]
                    print(f"Found android_version from MuMuManager.exe for -v {vindex}: {mumu_version}")
                    replaced_on_str = "nx_device/{}/shell/MuMuNxDevice.exe".format(mumu_version)
                    final_emulator_path = emulator_path.replace(replaced_off_str, replaced_on_str)
                    return final_emulator_path
            else:
                print(f"MuMuManager.exe returned non-zero exit code: {result.returncode}, stderr: {result.stderr}")
        except Exception as e:
            print(f"Error while running MuMuManager.exe: {e}")
        # 3. 根据 nx_device 目录下的版本号选择最新的版本
        # 则找到原路径中 nx_main 这一级路径的上一级文件夹，拼接访问 nx_device 下一共有几个版本，选择最新的版本
        try:
            versions = [entry.name for entry in os.scandir(nx_device_dir) if entry.is_dir()]
            print(f"Scanning nx_device directory: {nx_device_dir}, found versions: {list(versions)}")
            mumu_version = max(versions,key=lambda version: tuple(int(part) for part in version.split(".")),)
            replaced_on_str = "nx_device/{}/shell/MuMuNxDevice.exe".format(mumu_version)
            final_emulator_path = emulator_path.replace(replaced_off_str, replaced_on_str)
            return final_emulator_path
        except (OSError, ValueError) as e:
            print(f"Error while scanning nx_device directory: {e}")
        return final_emulator_path