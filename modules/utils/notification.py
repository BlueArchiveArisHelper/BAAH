from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import json

from requests import get as http_get
from requests import post as http_post
from modules.configs.MyConfig import config
from modules.utils.data_utils import decrypt_data


class Message_Sender:
    """
    消息发送的基类
    """
    def send(self, message: str, title: str = "BAAH通知"):
        pass
    
class Email_Sender(Message_Sender):
    """
    邮件发送类
    
    Parameters
    ==========
    mail_user: str
        发送者的账号
    mail_pass: str
        发送者的token
    sender: str
        发送者的邮箱
    receiver: str
        接收者的邮箱
    mail_host: str
        邮件服务器地址
    debug_int: int
        调试模式
    """
    def __init__(self, mail_user, mail_pass, sender, receiver, mail_host = 'smtp.qq.com', debug_int = 1):
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.sender = sender
        self.receiver = receiver
        self.mail_host = mail_host
        self.debug_int = debug_int
    
    def send(self, message: str, title: str = "BAAH通知") -> str:
        return self.send_mail(message, title)
        
    def send_mail(self, message, title):
        if self.mail_user == '' or self.mail_pass == '' or self.receiver == '' or self.mail_host == '':
            # 如果没有指定发送者的qq号或者授权码，则直接返回
            return '发送信息不全'
        #ssl登录
        smtp = SMTP_SSL(self.mail_host)
        #set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(self.debug_int)
        smtp.ehlo(self.mail_host)
        smtp.login(self.mail_user, self.mail_pass)

        msg = MIMEText(message, "plain", 'utf-8')
        msg["Subject"] = Header(title, 'utf-8')
        msg["From"] = self.sender
        msg["To"] = self.receiver
        res=smtp.sendmail(self.sender, self.receiver, msg.as_string())
        smtp.quit()
        try:
            print(res.split()[-6:])
        except:
            print("error when print email send result")
    
class Http_Sender(Message_Sender):
    """
    Api发送类
    """
    def __init__(self, target_url, token, token_pattern="[token]", is_get=True, content_pattern="[content]", title_pattern="[title]", content="{}") -> None:
        super().__init__()
        self.target_url = target_url
        self.token = token
        self.token_pattern = token_pattern
        self.is_get = is_get
        self.content_pattern = content_pattern
        self.title_pattern = title_pattern
        self.content = content
    
    def send(self, message: str, title: str = "BAAH通知") -> str:
        request_url = self.target_url.replace(self.token_pattern, self.token).replace(self.title_pattern, title).replace(self.content_pattern, message)
        if self.is_get:
            response = http_get(request_url)
        else:
            # 先解析 JSON，再替换字符串，避免通知中的引号、换行破坏请求体。
            def replace_content(value):
                if isinstance(value, str):
                    return value.replace(self.token_pattern, self.token).replace(self.title_pattern, title).replace(self.content_pattern, message)
                if isinstance(value, list):
                    return [replace_content(item) for item in value]
                if isinstance(value, dict):
                    return {replace_content(key): replace_content(item) for key, item in value.items()}
                return value

            request_body = replace_content(json.loads(self.content))
            headers = {'Content-Type': 'application/json;charset=utf-8'}
            response = http_post(request_url, json=request_body, headers=headers)
        if response.status_code == 200:
            # 自定义通知接口可能返回空响应、纯文本或不含 data 的 JSON。
            try:
                result = response.json()
            except ValueError:
                return
            if isinstance(result, dict) and result.get('data'):
                print(result['data'])

class Notificationer:
    """
    通知类，用于发送通知
    """
    def __init__(self):
        self.senders = []
        
    def add_sender(self, sender: Message_Sender):
        self.senders.append(sender)

    def send(self, message: str, title: str = "BAAH通知") -> str:
        for sender in self.senders:
            try:
                sender.send(message, title)
            except Exception as e:
                print("发送失败", e)
        return "发送结束，共有{}个通知器".format(len(self.senders))

# 实例化放在BAAH的生命周期里，每个配置文件邮箱可以不一样
def create_notificationer():
    """
    创建一个通知器
    """
    notificationer = Notificationer()
    # 构造邮件通知对象
    if config.userconfigdict["ENABLE_MAIL_NOTI"]:
        if config.userconfigdict['ADVANCED_EMAIL']:
            # 如果开启了高级模式，则用户自己定义所有的邮件发送参数
            email_sender = Email_Sender(
                config.userconfigdict['MAIL_USER'], 
                decrypt_data(config.userconfigdict['MAIL_PASS'], config.softwareconfigdict["ENCRYPT_KEY"]), 
                config.userconfigdict['SENDER_EMAIL'], 
                config.userconfigdict['RECEIVER_EMAIL'], 
                config.userconfigdict['MAIL_HOST'], 
                1
            )
        else:
            email_sender = Email_Sender(
                config.userconfigdict['MAIL_USER'], 
                decrypt_data(config.userconfigdict['MAIL_PASS'], config.softwareconfigdict["ENCRYPT_KEY"]), 
                config.userconfigdict['MAIL_USER']+"@qq.com", 
                config.userconfigdict['MAIL_USER']+"@qq.com", 
                'smtp.qq.com', 
                1)
        notificationer.add_sender(email_sender)
    # 构造第三方api通知对象
    if config.userconfigdict["ENABLE_HTTP_NOTI"]:
        http_sender = Http_Sender(
            config.userconfigdict['TARGET_HTTP_URL'],
            token=config.userconfigdict['TARGET_HTTP_TOKEN'],
            is_get=config.userconfigdict['WEB_NOTI_TYPE_GET_OR_POST'] == 0,
            content=config.userconfigdict['WEB_NOTI_POST_CONTENT']
        )
        notificationer.add_sender(http_sender)



    return notificationer
