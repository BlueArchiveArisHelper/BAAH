import sys
from modules.utils.log_utils import logging
from modules.configs.MyConfig import config
if len(sys.argv) > 1:
    configname = sys.argv[1]
    config.parse_user_config(configname)
    print("读取指定的config文件: "+configname)
else:
    configname = "config.json"
    config.parse_user_config(configname)
    print("读取默认config文件: "+configname)
# 图片截取&标注
import threading
import requests
import cv2
import os
import time
from modules.AllTask.SubTask.RaidQuest import RaidQuest
from modules.AllTask.SubTask.GridQuest import GridQuest
from modules.AllTask.SubTask.ScrollSelect import ScrollSelect
import numpy as np
from modules.AllTask.InCafe.InviteStudent import InviteStudent
from modules.AllTask.SubTask.FightQuest import FightQuest
from modules.AllTask.InCafe.TouchHead import TouchHead
from modules.utils import *
from DATA.assets.ButtonName import ButtonName
from DATA.assets.PageName import PageName
from DATA.assets.PopupName import PopupName

from modules.AllTask import *
from modules.AllTask.InCafe.CollectPower import CollectPower
from modules.AllPage.Page import Page


from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
from fgo import fgo_start
from hbr import hbr_start

if __name__=="__main__":
    # #sender_qq为发件人的qq号码
    # sender_qq = '1113746057'
    # #pwd为qq邮箱的授权码
    # pwd = ''
    # #收件人邮箱receiver
    # receiver='1113746057@qq.com'
    # #邮件的正文内容
    # mail_content = f'测试\n{config.userconfigdict["SERVER_TYPE"]}'
    # #邮件标题
    # mail_title = 'BAAH 测试'
    
    # send_mail(sender_qq=sender_qq,pwd=pwd,receiver=receiver,mail_title=mail_title,mail_content=mail_content)
    
    # print([i for i in os.listdir(config.USER_CONFIG_FOLDER) if i.endswith(".json")])
    
    # print(os.path.basename(config.userconfigdict['TARGET_EMULATOR_PATH']+" --instance pie"))
    
    # emulator_instance = subprocess_run(config.userconfigdict['TARGET_EMULATOR_PATH'].split(" "), isasync=True)
    # print("等待模拟器启动")
    # for i in range(10):
    #     time.sleep(1)
    #     print(".")
    # print("\n关闭模拟器")
    # # 关闭模拟器
    # subprocess_run(["taskkill", "/F", "/IM", "HD-Player.exe"], encoding="gbk")
    # print("成功关闭")
    # try:
    #     if not check_connect():
    #         print("请手动打开模拟器，adb连接失败，可能config.json端口配置有误")
    #     else:
    #         while 1:
    #             input("按回车键截图:")
    #             print("左键拖动区域截图，右键点击获取坐标点信息")
    #             screenshot()
    #             main()
    # except Exception as e:
    #     pass
    # input("按回车键退出")
    # print(os.path.getsize(f"./{'screenshot.png'}"))
    
    # request_url = "https://arona.diyigemt.com/api/v2/image?name=%E5%9B%BD%E9%99%85%E6%9C%8D%E6%B4%BB%E5%8A%A8"
    # response = requests.get(request_url)
    # if response.status_code == 200:
    #     if len(response.json()['data']) != 0:
    #         print(response.json()['data'])
    
    # connect_to_device()
    # screenshot()

    # print(Page.is_page(PageName.PAGE_CAFE))
    # print(match(button_pic(ButtonName.BUTTON_COLLECT_GRAY)))
    # print(match(button_pic(ButtonName.BUTTON_COLLECT_GRAY), returnpos=True)[2])
    # print(match(button_pic(ButtonName.BUTTON_COLLECT), returnpos=True)[2])
    
    # 测match
    # res1 = match_pattern(config.userconfigdict['SCREENSHOT_NAME'], page_pic(PageName.PAGE_GRID_FIGHT),  show_result=True, auto_rotate_if_trans=False)

    # 比划点
    # screencut_tool()
    # offset = 40
    
    
    # matchres = match_pixel((639, 240), Page.COLOR_RED)
    # print(matchres)
    
    # AutoStory().run()
    
    # 获取入口activity
    #config.parse_user_config("CN_hard.json")
    #print(get_now_running_app_entrance_activity())
    hbr_start()
    
    # 推图那一套
    # FightQuest(backtopic=page_pic(PageName.PAGE_EVENT)).run()
    
    # ga = GridAnalyzer("quest","7-3.json")
    
    # GridQuest(ga, lambda: match(page_pic(PageName.PAGE_QUEST_SEL)), require_type="0").run()
    
    # knn_positions, _, _ = ga.multikmeans(ga.get_mask(get_screenshot_cv_data(), ga.PIXEL_HEAD_YELLOW, shrink_kernels=[(4, 2), (2, 2)]), 1)
    # print(knn_positions[0][1], knn_positions[0][0])
    # cv2.imshow( "s", ga.get_mask(get_screenshot_cv_data(), ga.PIXEL_HEAD_YELLOW) )
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # screencut_tool()
    
    
    # 扫荡关卡识别地区数字
    # for i in range(20):
    #     screenshot()
    #     print(ocr_area((122, 179), (165, 211)))
    #     # click((1242, 357)) # right
    #     click((40, 357)) # left
    
    
    # 图像识别
    # rawMat = cv2.imread("./screenshot.png")
    # res = ocr_area((18, 50), (74, 87), multi_lines=True)
    # for i in range(10):
        # print(ocr_area((72, 85), (200, 114)))
    # reslist = ocr_area((72, 544), (91, 569), multi_lines=False)
    # print(reslist)
    
    # 测task
    # Event
    # ScrollSelect(7, 130, 235, 674, 1114,  lambda: match(popup_pic(PopupName.POPUP_TASK_INFO))).run()
    # special
    # ScrollSelect(11, 130, 230, 680, 1119, lambda: match(popup_pic(PopupName.POPUP_TASK_INFO))).run()
    # InEvent().run()
    # RaidQuest(-2).run()
    
    
    # 测透明图片的旋转
    # mypic = cv2.imread(button_pic(ButtonName.BUTTON_STU_NOTICE), cv2.IMREAD_UNCHANGED)
    # newpic = rotate_image_with_transparency(mypic, 90)
    # cv2.imshow("newpic", newpic)
    # cv2.waitKey(0)
    
    # 测找不同获取咖啡馆学生中心坐标
    # click((68, 649), 1)
    # screenshot()
    # noStu = cv2.imread(config.userconfigdict['SCREENSHOT_NAME'])
    # click((1171, 95), 1)
    # for i in range(10):
    #     screenshot()
    #     hasStu = cv2.imread(config.userconfigdict['SCREENSHOT_NAME'])
    #     diff_pos_list = compare_diff(noStu, hasStu, [1, 1279], [124, 568])
    #     print(diff_pos_list)
    #     for pos in diff_pos_list:
    #         cv2.circle(hasStu, pos, 10, (0, 0, 255), -1)
    #     cv2.imshow("newpic", hasStu)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    
    # 画3x3点
    # mypic = cv2.imread("./screenshot.png")
    # xs = np.linspace(299, 995, 3, dtype=int)
    # ys = np.linspace(268, 573, 3, dtype=int)
    
    # for row in range(len(ys)):
    #     for col in range(len(xs)):
    #         # 在点周围标数字
    #         cv2.putText(mypic, str(row*3+col), (xs[col], ys[row]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    #         cv2.circle(mypic, (xs[col], ys[row]), 10, (0, 0, 255), -1)
    # cv2.imshow("newpic", mypic)
    # cv2.waitKey(0)
    
    
    # # 截图小工具 screencut.exe
    # print("请手动打开模拟器...\nKeep emulator open")
    # sleep(2)
    # check_connect()
    # while 1:
    #     input(f"按回车键截图\nPress Enter to screencut:")
    #     print("左键拖动区域截图，右键点击获取坐标点信息\nTry left mouse drag or right mouse click")
    #     screenshot()
    #     screencut_tool()
    #     print("==========")
    
    # 走图识别start格子小工具
    # def get_kmeans(img, n, max_iter=5):
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     # 将img看成二维数组
    #     # 非0的像素点就是数据点
    #     # 为0的像素点就是背景
    #     # 随机n类，每类的中心点（x,y坐标）是随机的
    #     initial_centers = []
    #     for i in range(n):
    #         x = np.random.randint(0, img.shape[0])
    #         y = np.random.randint(0, img.shape[1])
    #         initial_centers.append([x, y])
    #     print("initial_centers", initial_centers)
        
    #     centers = initial_centers
    #     # 每次迭代，每个类的中心点都会更新
        
    #     # 将图像数组展平
    #     all_points = img.reshape((-1, 1))
    #     # 在axis=1的方向上，添加两列，range
    #     all_points = np.hstack((all_points, np.arange(all_points.shape[0]).reshape((-1, 1))))
    #     all_points = np.hstack((all_points, np.arange(all_points.shape[0]).reshape((-1, 1))))
        
    #     # 处理第2列数据除以图像宽度得到整数，处理第3列数据除以图像宽度得到余数
    #     all_points[:, 1] = all_points[:, 1] // img.shape[1]
    #     all_points[:, 2] = all_points[:, 2] % img.shape[1]
    #     # 在axis=1的方向上，添加一列，初始值为0，为每个像素点的类别
    #     all_points = np.hstack((all_points, np.zeros((all_points.shape[0], 1))))
    #     # 后续只考虑非0的像素点 np.any(img[i] != 0)
    #     # 去除第一列为0的像素点
    #     all_points = all_points[all_points[:, 0] != 0]
    #     print("all_points.shape", all_points.shape) # (n, 4)
        
    #     if all_points.shape[0] == 0:
    #         print("黄色过滤失败")
    #         return centers
        
    #     for i in range(max_iter):
    #         # 每次迭代，计算每个像素点到每个类的距离，取最小的那个类下标赋值给第4列
    #         for j in range(all_points.shape[0]):
    #             distances = []
    #             for k in range(len(centers)):
    #                 distances.append(np.linalg.norm(all_points[j, 1:3] - centers[k]))
    #             all_points[j, 3] = np.argmin(distances)
    #         # 每次迭代，计算每个类的中心点
    #         for j in range(len(centers)):
    #             # 取出第4列等于j的所有像素点
    #             points = all_points[all_points[:, 3] == j]
    #             # 计算平均值，如果没有像素点（空簇问题），就在其他簇内的点随机挑一个设为这个的中心点
    #             if points.shape[0] != 0:
    #                 centers[j] = np.mean(points[:, 1:3], axis=0)
    #             else:
    #                 centers[j] = all_points[np.random.randint(0, all_points.shape[0]), 1:3]
    #         print("iter centers", centers)
    #     return centers
        


    # # 画出k-means的结果
    # def draw_kmeans(img, centers):
    #     for center in centers:
    #         cv2.circle(img, (int(center[1]), int(center[0])), 15, (0, 0, 255), -1)
    #     return img

    # def show(img):
    #     # 左键点击获取BGRA值
    #     def on_mouse(event, x, y, flags, param):
    #         if event == cv2.EVENT_LBUTTONDOWN:
    #             print("BGR", img[y, x])
            
    #     cv2.namedWindow('image')
    #     cv2.setMouseCallback('image', on_mouse)
    #     cv2.imshow('image', img)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    # import numpy as np
    # print("请手动打开模拟器...\nKeep emulator open")
    # sleep(2)
    # check_connect()
    # while 1:
    #     numstr = input(f"输入黄色的开始格子数量\nInput number of start block:")
    #     try:
    #         num = int(numstr)
    #         assert num >= 1 and num <= 5
    #     except:
    #         print("输入有误，请重新输入\nInvalid input, try again")
    #         continue
    #     screenshot()
    #     # 读取
    #     img = cv2.imread("./{}".format(config.userconfigdict['SCREENSHOT_NAME']))
    #     # 黄色蒙版
    #     lower = np.array([125, 250, 250])
    #     upper = np.array([132, 255, 255])
    #     mask = cv2.inRange(img, lower, upper)
    #     # 转成灰度图
    #     mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    #     # 腐蚀
    #     kernel = np.ones((3, 3), np.uint8)
    #     masker2 = cv2.erode(mask, kernel)
    #     # k-means，维度是图片的xy坐标，将坐标相近的像素聚类
    #     centers = get_kmeans(masker2, n=num, max_iter=5)
    #     kmeans = draw_kmeans(img.copy(), centers)
    #     show(kmeans)
