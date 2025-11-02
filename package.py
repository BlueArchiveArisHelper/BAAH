from modules.configs.myversion import myversion, mychangelog
import sys
# 检查命令行参数
if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        # 当使用-v参数时，打印版本号并退出
        print(myversion)
    if sys.argv[1] == "-c":
        # -c, 打印changelog
        print(mychangelog)
    sys.exit(0)
import zipfile
import shutil
import os
import subprocess
from pathlib import Path
import nicegui
import time
import pponnxcr
import platform
import requests
import tarfile

def package_download_adb(platformstr = None):
    
    target_adb_path = os.path.join(os.getcwd(), "tools", "adb")
    downloadurls = {
        "Windows": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
        "Darwin": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
        "Linux": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
    }
    if not os.path.exists(target_adb_path):
        if platformstr and platformstr in downloadurls.keys():
            url = downloadurls[platformstr]
        elif platform.system() in downloadurls.keys():
            url = downloadurls[platform.system()]
        else:
            print(f"Unknown platform: {platform.system()}")
            return
        
        # download zip
        r = requests.get(url)
        with open("platform-tools-latest.zip", "wb") as f:
            f.write(r.content)
        target_adb_path_parent_folder = os.path.dirname(target_adb_path)
        # unzip to target_adb_path, rename the upper folder "playform-tools" to "adb"
        with zipfile.ZipFile("platform-tools-latest.zip", 'r') as z:
            z.extractall(target_adb_path_parent_folder)
        print(f"adb downloaded to: {target_adb_path_parent_folder}")
        package_rename(os.path.join(target_adb_path_parent_folder, "platform-tools"), target_adb_path)
        
        
    else:
        print(f"adb already exists: {target_adb_path}")

def package_download_aria2(platformstr = None):
    tools_base_path = os.path.join(os.getcwd(), "tools")
    target_aria2_path = os.path.join(tools_base_path, "aria2")
    downloadurls = {
        "Windows": "https://gh-proxy.com/github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip",
        "Linux": "https://gh-proxy.com/github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0.tar.gz"
    }
    if not os.path.exists(target_aria2_path):
        if platformstr and platformstr in downloadurls.keys():
            url = downloadurls[platformstr]
        elif platform.system() in downloadurls.keys():
            url = downloadurls[platform.system()]
        else:
            print(f"Unknown platform: {platform.system()}")
            return
        
        # download zip/tar
        r = requests.get(url)
        if platformstr == "Windows":
            with open('aria2.zip', "wb") as f:
                f.write(r.content)
            # unzip to target_aria2_path, rename the upper folder "aria2-1.37.0-win-64bit-build1" to "aria2"
            with zipfile.ZipFile("aria2.zip", 'r') as z:
                z.extractall(tools_base_path)
            print(f"aria2 downloaded to: {tools_base_path}")
            package_rename(os.path.join(tools_base_path, "aria2-1.37.0-win-64bit-build1"), target_aria2_path)
        if platformstr == "Linux":
            with open('aria2.tar.gz', "wb") as f:
                f.write(r.content)
            # untar to target_aria2_path, rename the upper folder "aria2-1.37.0" to "aria2"
            with tarfile.open("aria2.tar.gz", 'r') as z:
                z.extractall(tools_base_path)
            print(f"aria2 downloaded to: {tools_base_path}")
            package_rename(os.path.join(tools_base_path, "aria2-1.37.0"), target_aria2_path)
            
    else:
        print(f"aria2 already exists: {target_aria2_path}")

def package_copyfolder(src, dst):
    try:
        # 拷贝文件夹
        shutil.copytree(src, dst)
        print(f"{dst}文件夹已拷贝")
    except FileExistsError as e:
        print(f"{dst}文件夹已存在!")

def package_copyfile(src, dst):
    try:
        shutil.copyfile(src, dst)
        print(f"{dst}已拷贝")
    except FileExistsError as e:
        print(f"{dst}已存在!")

def package_rename(src, dst):
    try:
        os.rename(src, dst)
    except Exception as e:
        print(f"{dst}已存在!")
        
def package_create_folder(path):
    try:
        os.makedirs(path)
    except Exception as e:
        print(f"{path}创建时出错!")

def package_remove_file(path):
    try:
        os.remove(path)
    except Exception as e:
        print(f"{path}删除时出错!")

def package_remove_folder(path):
    try:
        shutil.rmtree(path)
    except Exception as e:
        print(f"{path}删除时出错!")

# ====================开始====================

config_version = myversion

# mainly for windows, download adb
package_download_adb(platformstr="Windows")
# mainly for windows, download aria2
package_download_aria2(platformstr="Windows")


package_remove_folder("./dist")


# 打包GUI
guicmd = [
    'pyinstaller',
    'jsoneditor.py',
    '-n', 'BAAH',  # 1.11.0 GUI包含了script内容，把GUI打包为BAAH.exe
    # '--windowed', # prevent console appearing, only use with ui.run(native=True, ...)
    '--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui',
    '--add-data', f'{Path(pponnxcr.__file__).parent}{os.pathsep}pponnxcr',
    '--icon', './DATA/icons/aris.ico',
    '-y'
]
subprocess.call(guicmd)

# 打包update.py，名字为BAAH_UPDATE
updatecmd = [
    'pyinstaller',
    'update.py',
    '-n', 'BAAH_UPDATE',
    '--icon', './DATA/icons/kayoko.ico',
    '-y'
]
subprocess.call(updatecmd)

# 当前目录
print("当前目录：", os.getcwd())
workdir = os.getcwd()

print("开始封装")


package_copyfolder('./tools/adb', './dist/BAAH/tools/adb')
package_copyfolder('./tools/aria2', './dist/BAAH/tools/aria2')

# pytinstall的时候已经把pponnxcr和nicegui文件拷贝进去了
# package_copyfolder('./tools/pponnxcr', './dist/BAAH/_internal/pponnxcr')

# 挪i18n进去创建下DATA文件夹
package_copyfolder("./DATA/i18n", "./dist/BAAH/DATA/i18n")

package_create_folder("./dist/BAAH/DATA/CONFIGS")
# 将LICENSE挪进去占位, 不放software.config, 防止覆盖掉用户的
package_copyfile("./LICENSE", "./dist/BAAH/DATA/CONFIGS/LICENSE")

# 这里只拷贝example.json，不拷贝其他的，因为其他的是用户的配置文件
# package_copyfolder("./BAAH_CONFIGS", "./dist/BAAH/BAAH_CONFIGS")
package_create_folder("./dist/BAAH/BAAH_CONFIGS")
package_copyfile("./BAAH_CONFIGS/example.json", "./dist/BAAH/BAAH_CONFIGS/example.json")

package_copyfolder("./DATA/assets", "./dist/BAAH/DATA/assets")
package_copyfolder("./DATA/assets_jp", "./dist/BAAH/DATA/assets_jp")
package_copyfolder("./DATA/assets_cn", "./dist/BAAH/DATA/assets_cn")
package_copyfolder("./DATA/assets_global_en", "./dist/BAAH/DATA/assets_global_en")
package_copyfolder("./DATA/grid_solution", "./dist/BAAH/DATA/grid_solution")
package_copyfile("./DATA/touch.zip", "./dist/BAAH/DATA/touch.zip")
package_copyfile("./dist/BAAH_UPDATE/BAAH_UPDATE.exe", "./dist/BAAH/BAAH_UPDATE.exe")

time.sleep(2)


package_rename("./dist/BAAH", f"./dist/BAAH{config_version}")

print("开始压缩")
time.sleep(2)

# 压缩./dist/BAAH文件夹为BAAH.zip
z = zipfile.ZipFile(f'./dist/BAAH{config_version}.zip', 'w', zipfile.ZIP_DEFLATED)
startdir = f"./dist/BAAH{config_version}"
for dirpath, dirnames, filenames in os.walk(startdir):
    for filename in filenames:
        z.write(os.path.join(dirpath, filename), arcname=os.path.join(dirpath, filename).replace("/dist",""))

print(f"完成，压缩包./dist/BAAH{config_version}.zip已生成")
print(f"压缩包大小为{os.path.getsize(f'./dist/BAAH{config_version}.zip')/1024/1024:.2f}MB")

# 压缩./dist/BAAH文件夹(除了_internal, tools)为BAAH_update.zip
z = zipfile.ZipFile(f'./dist/BAAH{config_version}_update.zip', 'w', zipfile.ZIP_DEFLATED)
startdir = f"./dist/BAAH{config_version}"
for dirpath, dirnames, filenames in os.walk(startdir):
    # 历史遗留问题，1.6.6之前打包的版本的实际pyinstaller版本过老.
    # 新版本打更新包需要额外添加_internal/jaraco/text文件夹内lorem文件
    if "_internal" in dirpath and "jaraco" in dirpath and "text" in dirpath:
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), arcname=os.path.join(dirpath, filename).replace("/dist",""))
    if "_internal" in dirpath or "tools" in dirpath or "BAAH_CONFIGS" in dirpath:
        continue
    for filename in filenames:
        z.write(os.path.join(dirpath, filename), arcname=os.path.join(dirpath, filename).replace("/dist",""))

print(f"完成，压缩包./dist/BAAH{config_version}_update.zip已生成")
print(f"压缩包大小为{os.path.getsize(f'./dist/BAAH{config_version}_update.zip')/1024/1024:.2f}MB")

