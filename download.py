from urllib.request import urlretrieve
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import ssl
import socket
import time

api_urls = {
    "JP": [
        "https://baah.hitfun.top/apk/jp",
        "https://api.blockhaity.qzz.io/baapk/jp",
        "https://blockhaity-api.netlify.app/baapk/jp",
    ],
    "GLOBAL": [
        "https://baah.hitfun.top/apk/global",
        "https://api.blockhaity.qzz.io/baapk/global",
        "https://blockhaity-api.netlify.app/baapk/global",
    ],
    "CN": "html://https://mumu.163.com/games/22367.html",
    "CN_BILI": "json://https://line1-h5-pc-api.biligame.com/game/detail/gameinfo?game_base_id=109864",
}

direct_get_urls = [
    "https://api.blockhaity.qzz.io/api/baapk.json",
    "https://blockhaity-api.netlify.app/api/baapk.json",
]

def get_final_url(url, timeout=10, retry_count=3):
        """
        获取URL重定向后的最终链接
    
        参数:
            url (str): 要检查的URL
            timeout (int): 请求超时时间(秒)
            retry_count (int): 失败重试次数
        
        返回:
            str: 最终URL或None(如果失败)
        """
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
        # 尝试多次请求
        for attempt in range(retry_count):
            try:
                # 创建请求对象
                request = Request(url, headers=headers)
            
                # 创建SSL上下文，用于处理HTTPS
                context = ssl.create_default_context()
            
                # 打开URL，设置超时和SSL上下文
                # urllib默认会处理重定向，不需要额外设置
                response = urlopen(request, timeout=timeout, context=context)

                # 获取最终URL和状态码
                final_url = response.geturl()
                status_code = response.getcode()
               
                print(f"请求成功，状态码: {status_code}")
                print(f"最终URL: {final_url}")
            
                return final_url
            
            except HTTPError as e:
                print(f"HTTP错误: {e.code} {e.reason}")
            
                # 对于HTTP错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except URLError as e:
                # 处理URL错误，包括DNS解析失败
                print(f"URL错误: {e.reason}")
            
                # 检查是否是DNS解析错误
                if isinstance(e.reason, socket.gaierror) and "Name or service not known" in str(e.reason):
                    print("\n检测到DNS解析问题")

                    # 对于DNS错误，不再重试
                    return None
                
                # 对于其他URL错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except socket.timeout as e:
                print(f"请求超时: {e}")
            
                # 对于超时错误，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None
            
            except Exception as e:
                print(f"发生错误: {e}")
            
                # 对于其他异常，等待一段时间后重试
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                return None

url = get_final_url("https://api.blockhaity.qzz.io/api/baapk/jp")
print(url)